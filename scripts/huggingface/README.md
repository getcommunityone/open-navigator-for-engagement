# HuggingFace Dataset Management

Scripts for preparing and uploading datasets to HuggingFace.

## Preparation

### reorganize_for_huggingface.py
Reorganizes data files into HuggingFace-compatible structure.

**Usage:**
```bash
python scripts/huggingface/reorganize_for_huggingface.py
```

### finalize_huggingface_structure.py
Final validation and preparation of HuggingFace datasets.

**Usage:**
```bash
python scripts/huggingface/finalize_huggingface_structure.py
```

## Upload Scripts

### upload_to_huggingface.py
**Main upload script** - uploads all datasets to HuggingFace.

**Usage:**
```bash
python scripts/huggingface/upload_to_huggingface.py
```

**Requirements:**
- HuggingFace token in environment
- HF_ORGANIZATION set in .env

### Specific Uploads

- `upload_nonprofits_to_hf.py` - Upload nonprofit datasets
- `upload_meetings_to_hf.py` - Upload meeting datasets
- `upload_state_splits_to_hf.py` - Upload state-partitioned data

## Workflow

1. Prepare data: `reorganize_for_huggingface.py`
2. Finalize: `finalize_huggingface_structure.py`
3. Upload: `upload_to_huggingface.py`

## Environment Variables

Required in `.env`:
```bash
HF_ORGANIZATION=CommunityOne
HF_USERNAME=CommunityOne
HF_TOKEN=hf_...
```
