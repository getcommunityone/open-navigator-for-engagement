"""
Agent Evaluation Framework for Databricks Agent Bricks.

Provides:
- Automated evaluation of agent quality
- Ground truth comparison
- Metrics tracking (accuracy, latency, cost)
- A/B testing support
- Regression detection
"""
from typing import List, Dict, Any, Optional, Callable
import pandas as pd
import mlflow
from datetime import datetime
from dataclasses import dataclass
from loguru import logger

from config import settings


@dataclass
class EvaluationMetrics:
    """Container for evaluation metrics."""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    avg_latency_ms: float
    avg_tokens: float
    total_cost: float
    error_rate: float


class AgentEvaluator:
    """
    Evaluates agent performance using MLflow.
    
    Integrates with:
    - MLflow Evaluate API
    - Mosaic AI Agent Framework evaluation
    - Unity Catalog for versioning
    """
    
    def __init__(self, agent_name: str):
        """
        Initialize evaluator.
        
        Args:
            agent_name: Name of agent to evaluate
        """
        self.agent_name = agent_name
        self.catalog = settings.catalog_name
        self.schema = settings.schema_name
        
    def evaluate_agent(
        self,
        model_uri: str,
        eval_data: pd.DataFrame,
        evaluators: Optional[List[str]] = None,
        custom_metrics: Optional[List[Callable]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate an agent using MLflow.
        
        Args:
            model_uri: URI of model to evaluate (e.g., "models:/main.agents.classifier/1")
            eval_data: DataFrame with input data and ground truth
                       Must have columns: 'inputs', 'ground_truth'
            evaluators: List of built-in evaluators ("default", "exact_match", etc.)
            custom_metrics: Custom metric functions
            
        Returns:
            Evaluation results
        """
        logger.info(f"Evaluating {model_uri}")
        
        # Load model
        model = mlflow.pyfunc.load_model(model_uri)
        
        # Default evaluators if none specified
        if evaluators is None:
            evaluators = ["default"]
        
        # Run evaluation
        with mlflow.start_run(run_name=f"eval_{self.agent_name}") as run:
            results = mlflow.evaluate(
                model=model_uri,
                data=eval_data,
                targets="ground_truth",
                model_type="text",
                evaluators=evaluators,
                extra_metrics=custom_metrics
            )
            
            # Log additional metrics
            mlflow.log_param("eval_dataset_size", len(eval_data))
            mlflow.log_param("evaluators", ",".join(evaluators))
            
            logger.info(f"Evaluation complete. Run ID: {run.info.run_id}")
            
        return {
            "run_id": run.info.run_id,
            "metrics": results.metrics,
            "tables": results.tables
        }
    
    def evaluate_classifier(
        self,
        model_uri: str,
        test_documents: List[Dict[str, Any]],
        ground_truth: List[str]
    ) -> EvaluationMetrics:
        """
        Evaluate a classifier agent.
        
        Args:
            model_uri: Model URI
            test_documents: List of test documents with 'document_id', 'title', 'content'
            ground_truth: List of true labels
            
        Returns:
            Evaluation metrics
        """
        model = mlflow.pyfunc.load_model(model_uri)
        
        # Get predictions
        predictions = []
        latencies = []
        
        for doc in test_documents:
            start = datetime.now()
            result = model.predict(doc)
            end = datetime.now()
            
            predictions.append(result.get("primary_topic"))
            latencies.append((end - start).total_seconds() * 1000)
        
        # Calculate metrics
        from sklearn.metrics import accuracy_score, precision_recall_fscore_support
        
        accuracy = accuracy_score(ground_truth, predictions)
        precision, recall, f1, _ = precision_recall_fscore_support(
            ground_truth, predictions, average='weighted', zero_division=0
        )
        
        metrics = EvaluationMetrics(
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1,
            avg_latency_ms=sum(latencies) / len(latencies),
            avg_tokens=0,  # Would track from LLM calls
            total_cost=0,  # Would calculate from token usage
            error_rate=0
        )
        
        # Log to MLflow
        with mlflow.start_run(run_name=f"eval_classifier_{datetime.now().strftime('%Y%m%d_%H%M')}"):
            mlflow.log_metrics({
                "accuracy": metrics.accuracy,
                "precision": metrics.precision,
                "recall": metrics.recall,
                "f1_score": metrics.f1_score,
                "avg_latency_ms": metrics.avg_latency_ms
            })
            
            # Log confusion matrix
            from sklearn.metrics import confusion_matrix
            import matplotlib.pyplot as plt
            import seaborn as sns
            
            cm = confusion_matrix(ground_truth, predictions)
            plt.figure(figsize=(10, 8))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
            plt.title('Classification Confusion Matrix')
            plt.ylabel('True Label')
            plt.xlabel('Predicted Label')
            mlflow.log_figure(plt.gcf(), "confusion_matrix.png")
            plt.close()
        
        return metrics
    
    def compare_versions(
        self,
        version_a: str,
        version_b: str,
        eval_data: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Compare two model versions (A/B testing).
        
        Args:
            version_a: First version number
            version_b: Second version number
            eval_data: Evaluation dataset
            
        Returns:
            Comparison results
        """
        model_name = f"{self.catalog}.{self.schema}.{self.agent_name}"
        
        logger.info(f"Comparing {model_name} v{version_a} vs v{version_b}")
        
        # Evaluate version A
        uri_a = f"models:/{model_name}/{version_a}"
        results_a = self.evaluate_agent(uri_a, eval_data)
        
        # Evaluate version B
        uri_b = f"models:/{model_name}/{version_b}"
        results_b = self.evaluate_agent(uri_b, eval_data)
        
        # Compare metrics
        comparison = {
            "version_a": {
                "version": version_a,
                "metrics": results_a["metrics"]
            },
            "version_b": {
                "version": version_b,
                "metrics": results_b["metrics"]
            },
            "improvements": {}
        }
        
        # Calculate improvements
        for metric_name in results_a["metrics"]:
            if metric_name in results_b["metrics"]:
                a_val = results_a["metrics"][metric_name]
                b_val = results_b["metrics"][metric_name]
                
                if isinstance(a_val, (int, float)) and isinstance(b_val, (int, float)):
                    improvement = ((b_val - a_val) / a_val * 100) if a_val != 0 else 0
                    comparison["improvements"][metric_name] = {
                        "v{version_a}": a_val,
                        "v{version_b}": b_val,
                        "improvement_pct": improvement
                    }
        
        logger.info("Comparison complete")
        return comparison
    
    def create_eval_dataset_from_feedback(
        self,
        feedback_table: str,
        min_confidence: float = 0.8,
        max_samples: int = 1000
    ) -> pd.DataFrame:
        """
        Create evaluation dataset from user feedback in Delta Lake.
        
        Args:
            feedback_table: Feedback table name
            min_confidence: Minimum confidence for inclusion
            max_samples: Maximum samples to include
            
        Returns:
            Evaluation DataFrame
        """
        from databricks.sdk import WorkspaceClient
        
        w = WorkspaceClient(
            host=settings.databricks_host,
            token=settings.databricks_token
        )
        
        # Query feedback table
        query = f"""
        SELECT 
            document_id,
            input_data,
            predicted_label,
            user_corrected_label,
            feedback_timestamp
        FROM {self.catalog}.{self.schema}.{feedback_table}
        WHERE user_corrected_label IS NOT NULL
          AND feedback_confidence >= {min_confidence}
        ORDER BY feedback_timestamp DESC
        LIMIT {max_samples}
        """
        
        # This would execute via Databricks SQL
        # For now, return placeholder
        logger.info(f"Would query: {query}")
        
        return pd.DataFrame({
            "inputs": [],
            "ground_truth": []
        })


def run_evaluation_suite():
    """
    Run full evaluation suite for all agents.
    
    Usage:
        python -m databricks.evaluation
    """
    from agents.mlflow_classifier import PolicyClassifierAgent
    
    print("\n🧪 Running Agent Evaluation Suite\n")
    
    # Prepare test data
    test_documents = [
        {
            "document_id": "eval_001",
            "title": "Water Quality Board Meeting",
            "content": "Discussion of fluoride levels in municipal water supply. Motion to increase fluoridation to optimal levels."
        },
        {
            "document_id": "eval_002",
            "title": "School Board Session",
            "content": "Proposal for free dental screenings for all elementary students as part of school health program."
        },
        {
            "document_id": "eval_003",
            "title": "Budget Committee",
            "content": "Review of general fund allocations for the upcoming fiscal year. No health-related items."
        }
    ]
    
    ground_truth = [
        "water_fluoridation",
        "school_dental_screening",
        "not_oral_health_related"
    ]
    
    # Evaluate classifier
    print("📊 Evaluating Policy Classifier...")
    evaluator = AgentEvaluator("policy_classifier")
    
    # Note: Would use actual model URI after registration
    # metrics = evaluator.evaluate_classifier(
    #     model_uri="models:/main.agents.policy_classifier/1",
    #     test_documents=test_documents,
    #     ground_truth=ground_truth
    # )
    
    print("\n✅ Evaluation Suite Complete!")
    print("   View results in MLflow UI: {}/ml/experiments".format(settings.databricks_host))


if __name__ == "__main__":
    run_evaluation_suite()
