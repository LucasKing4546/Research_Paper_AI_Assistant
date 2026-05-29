import unittest

from mapper import NormalizedPaper, deduplicate_papers, map_core, map_semantic_scholar


class TestDeduplicationPipeline(unittest.TestCase):
	def test_map_semantic_scholar_normalizes_fields(self):
		raw_data = {
			"data": [
				{
					"paperId": "s2-paper-1",
					"externalIds": {"DOI": "10.1000/example-doi"},
					"title": "Few-shot learning in NLP",
					"authors": [{"name": "Alice"}, {"name": "Bob"}],
					"year": 2022,
					"abstract": "An example abstract.",
				}
			]
		}

		papers = map_semantic_scholar(raw_data)

		self.assertEqual(len(papers), 1)
		paper = papers[0]
		self.assertEqual(paper.id, "10.1000/example-doi")
		self.assertEqual(paper.title, "Few-shot learning in NLP")
		self.assertEqual(paper.authors, ["Alice", "Bob"])
		self.assertEqual(paper.year, 2022)
		self.assertEqual(paper.abstract, "An example abstract.")
		self.assertEqual(paper.source, "Semantic Scholar")
		self.assertEqual(paper.url, "https://www.semanticscholar.org/paper/s2-paper-1")

	def test_map_core_normalizes_fields(self):
		raw_data = {
			"results": [
				{
					"id": 123,
					"arxivId": "arXiv:1905.09718",
					"title": "Few-shot learning in NLP",
					"authors": [{"name": "Carol"}],
					"publishedDate": "2021-04-15",
					"abstract": "Another example abstract.",
					"downloadUrl": "https://example.com/download",
				}
			]
		}

		papers = map_core(raw_data)

		self.assertEqual(len(papers), 1)
		paper = papers[0]
		self.assertEqual(paper.id, "arXiv:1905.09718")
		self.assertEqual(paper.title, "Few-shot learning in NLP")
		self.assertEqual(paper.authors, ["Carol"])
		self.assertEqual(paper.year, 2021)
		self.assertEqual(paper.abstract, "Another example abstract.")
		self.assertEqual(paper.source, "CORE")
		self.assertEqual(paper.url, "https://example.com/download")

	def test_deduplicate_papers_removes_duplicates_by_id_and_title(self):
		papers = [
			NormalizedPaper(
				id="10.1000/example-doi",
				title="Few-shot learning in NLP",
				authors=["Alice"],
				year=2022,
				abstract="First version.",
				source="Semantic Scholar",
				url="https://example.com/s2",
			),
			NormalizedPaper(
				id="10.1000/example-doi",
				title="Few-shot learning in NLP",
				authors=["Carol"],
				year=2021,
				abstract="Duplicate by DOI.",
				source="CORE",
				url="https://example.com/core",
			),
			NormalizedPaper(
				id="another-id",
				title="A different paper",
				authors=["Dan"],
				year=2020,
				abstract="Different paper.",
				source="CORE",
				url=None,
			),
		]

		deduplicated = deduplicate_papers(papers)

		self.assertEqual(len(deduplicated), 2)
		self.assertEqual(deduplicated[0].id, "10.1000/example-doi")
		self.assertEqual(deduplicated[1].title, "A different paper")

	def test_deduplicate_papers_is_case_insensitive_on_titles(self):
		papers = [
			NormalizedPaper(
				id="paper-a",
				title="Few-Shot Learning in NLP",
				authors=["Alice"],
				year=2022,
				abstract="First version.",
				source="Semantic Scholar",
				url=None,
			),
			NormalizedPaper(
				id="paper-b",
				title="few-shot learning in nlp",
				authors=["Bob"],
				year=2021,
				abstract="Duplicate title with different case.",
				source="CORE",
				url=None,
			),
		]

		deduplicated = deduplicate_papers(papers)

		self.assertEqual(len(deduplicated), 1)
		self.assertEqual(deduplicated[0].title, "Few-Shot Learning in NLP")


if __name__ == "__main__":
	unittest.main(verbosity=2)