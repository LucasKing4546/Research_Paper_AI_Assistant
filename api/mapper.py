from dataclasses import dataclass, asdict
from typing import List, Optional
import json

# ==========================================
# 1. THE UNIFIED BLUEPRINT
# ==========================================
@dataclass
class NormalizedPaper:
    """
    The standard format that Paul and Vlad's Vector Store will expect.
    Every paper, regardless of source, gets squashed into this structure.
    """
    id: str                # A unique ID (DOI, arXiv ID, or Semantic Scholar ID)
    title: str
    authors: List[str]
    year: Optional[int]
    abstract: str
    source: str            # "Semantic Scholar", "CORE", or "arXiv"
    url: Optional[str]     # Link to the paper if available

    def to_json(self):
        """Converts the object back to a dictionary for easy debugging/storage."""
        return asdict(self)


# ==========================================
# 2. THE MAPPERS
# ==========================================

def map_semantic_scholar(raw_s2_data: dict) -> List[NormalizedPaper]:
    """Translates Semantic Scholar JSON into NormalizedPaper objects."""
    normalized_list = []
    if not raw_s2_data:
        return normalized_list
    
    # Check if the data exists
    papers = raw_s2_data.get("data", [])
    if not papers:
        return normalized_list

    for paper in papers:
        # Extract authors safely
        raw_authors = paper.get("authors", [])
        author_names = [author.get("name") for author in raw_authors if author.get("name")]
        
        # Determine the best ID (prefer DOI, fallback to S2's paperId)
        external_ids = paper.get("externalIds", {})
        best_id = external_ids.get("DOI") or paper.get("paperId", "unknown_id")
        
        # Build the standardized object
        normalized_paper = NormalizedPaper(
            id=best_id,
            title=paper.get("title", "Unknown Title"),
            authors=author_names,
            year=paper.get("year"),
            abstract=paper.get("abstract") or "No abstract available.",
            source="Semantic Scholar",
            url=f"https://www.semanticscholar.org/paper/{paper.get('paperId')}" if paper.get('paperId') else None
        )
        normalized_list.append(normalized_paper)
        
    return normalized_list


def map_core(raw_core_data: dict) -> List[NormalizedPaper]:
    """Translates CORE JSON into NormalizedPaper objects."""
    normalized_list = []
    if not raw_core_data:
        return normalized_list
    
    papers = raw_core_data.get("results", [])
    if not papers:
        return normalized_list

    for paper in papers:
        # Extract authors safely
        raw_authors = paper.get("authors", [])
        author_names = [author.get("name") for author in raw_authors if author.get("name")]
        
        # Extract year from publishedDate (usually a string like '2021-04-15')
        year = None
        pub_date = paper.get("publishedDate")
        if pub_date and len(pub_date) >= 4:
            try:
                year = int(pub_date[:4])
            except ValueError:
                pass
        
        # Determine the best ID (prefer DOI, fallback to arxivId or CORE ID)
        best_id = paper.get("doi") or paper.get("arxivId") or str(paper.get("id", "unknown_id"))
        
        # Build the standardized object
        normalized_paper = NormalizedPaper(
            id=best_id,
            title=paper.get("title", "Unknown Title"),
            authors=author_names,
            year=year,
            abstract=paper.get("abstract") or "No abstract available.",
            source="CORE",
            url=paper.get("downloadUrl") or paper.get("sourceUrl")
        )
        normalized_list.append(normalized_paper)
        
    return normalized_list

def deduplicate_papers(papers: List[NormalizedPaper]) -> List[NormalizedPaper]:
    """
    Takes a combined list of papers from all APIs and removes duplicates.
    Prioritizes matching by ID (DOI/arXiv ID), with a fallback to exact Title matches.
    """
    seen_ids = set()
    seen_titles = set()
    unique_papers = []

    for paper in papers:
        # Normalize the strings to lowercase to avoid case-sensitive mismatches
        safe_id = str(paper.id).strip().lower() if paper.id else ""
        safe_title = str(paper.title).strip().lower() if paper.title else ""

        # Skip if we have no ID and no Title (corrupted data)
        if not safe_id and not safe_title:
            continue

        # Check if we have already seen this ID or Title
        if (safe_id and safe_id in seen_ids) or (safe_title and safe_title in seen_titles):
            continue  # It's a duplicate, skip it

        # If it's unique, add it to our clean list and record its fingerprints
        unique_papers.append(paper)
        if safe_id:
            seen_ids.add(safe_id)
        if safe_title:
            seen_titles.add(safe_title)

    return unique_papers


# ==========================================
# HOW TO USE IT IN YOUR EXECUTION BLOCK
# ==========================================


# ==========================================
# 3. TEST EXECUTION
# ==========================================
    clean_s2 = map_semantic_scholar(dummy_s2_data)

