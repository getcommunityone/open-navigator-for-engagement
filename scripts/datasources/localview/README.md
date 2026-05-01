# LocalView Meeting Transcripts Scripts

Scripts for working with [LocalView](https://localview.net/) municipal meeting transcripts and agendas.

## Data Source

- **Website**: https://localview.net/
- **Coverage**: 200+ US municipalities
- **Data Types**: Meeting transcripts, agendas, attendees

## Scripts

- `localview_ingestion.py` - Ingest LocalView meeting data

## Data Includes

- Meeting transcripts (full text)
- Meeting agendas and documents
- Attendee lists
- Meeting metadata (date, location, type)

## Usage

```bash
python localview_ingestion.py --jurisdiction "Cambridge, MA"
```
