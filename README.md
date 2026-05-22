# Research Paper Q&A Agent

### Team **Verity** : [ Secara Lucas Victor, Petras Kevin Andrei, Rat Paul ] 

---
## 1. Introduction
The volume of scientific literature published each year has grown to a point where keeping up with the state of the art in any field is increasingly difficult. Researchers, students, and practitioners often need to sift through dozens of papers to find answers to specific questions, a process that is time-consuming and error-prone.
 
This project proposes a **Research Paper Q&A Agent**, a conversational system that accepts a natural language question from the user, retrieves relevant research papers from the web, and produces a grounded answer with exact citations pointing to the specific passages from which the answer was derived. The system functions as an intelligent research assistant: the user asks, the agent searches, reads, and responds with evidence.
 
This problem is relevant because it sits at the intersection of information retrieval and language understanding, and has direct practical value for anyone doing literature review or evidence-based research.

---
## 2. Problem Definition
**Input:** A natural language question posed by the user (e.g., *"What are the main approaches to few-shot learning in NLP?"*).
 
**Output:** A structured natural language answer accompanied by citations, where each cited passage is identified at the sentence or paragraph level, including the source paper title, authors, and year.
 
**Task type:** Open-domain question answering with retrieval (extractive + abstractive generation).
 
**Constraints and challenges:**
 
- Retrieved documents are long and heterogeneous in structure (abstracts, methods, results sections).
- The system must attribute answers faithfully; hallucinated or mis-attributed citations are a critical failure mode.
- Latency must be reasonable for interactive use.
- Coverage depends on the availability and accessibility of papers via public APIs (e.g., Semantic Scholar, arXiv).

---
## 3. State of the Art
 
The problem touches several active research areas:
 
1. **Lewis et al. (2020) - Retrieval-Augmented Generation (RAG):** Introduced the foundational RAG framework combining a dense retriever (DPR) with a seq2seq generator (BART). Demonstrated strong performance on open-domain QA benchmarks. [https://arxiv.org/abs/2005.11401]
2. **Guu et al. (2020) - REALM:** A retrieval-enhanced pre-training method that jointly trains a retriever and language model, improving knowledge-grounded generation. [https://arxiv.org/abs/2002.08909]
3. **Izacard & Grave (2021) - Fusion-in-Decoder (FiD):** Processes multiple retrieved passages independently through an encoder and fuses them in the decoder, significantly improving multi-document QA. [https://arxiv.org/abs/2007.01282]
4. **Nakano et al. (2021) - WebGPT:** Fine-tuned GPT-3 to browse the web, cite sources, and answer questions - closely related to the "search and cite" paradigm we adopt. [https://arxiv.org/abs/2112.09332]
5. **Xiong et al. (2021) - Approximate Nearest Neighbor Negative Contrastive Estimation (ANCE):** Improved dense retrieval for passage-level search, directly applicable to paper chunk retrieval. [https://arxiv.org/abs/2010.02666 ]

Current systems (e.g., Perplexity AI, Elicit, Consensus) apply similar ideas in production but are not open, domain-specific, or designed with fine-grained passage-level citation as a first-class requirement.

---
## 4. Proposed Solution 
The agent follows a **Retrieval-Augmented Generation (RAG)** pipeline:
 
1. **Query Understanding:** The user's question is parsed and optionally expanded (e.g., synonym injection, entity extraction) to improve retrieval recall.
2. **Multi-Source Retrieval:** The query is encoded using a dense encoder. Papers are fetched in parallel from multiple sources:

   | Source | Coverage | API |
   |---|---|---|
   | **arXiv** | CS, AI, Math, Physics | Free, full-text PDFs |
   | **Semantic Scholar** | All domains | Free, abstracts + metadata |
   | **PubMed Central** | Biomedical / Life Sciences | Free, full-text via Entrez |
   | **CORE** | All domains (open access) | Free, full-text aggregator |

   Results are deduplicated by DOI/title and normalized into a unified schema (title, authors, year, abstract, full-text chunks). Chunks are embedded and retrieved by cosine similarity via a vector store.

3. **Re-ranking:** Retrieved chunks are re-ranked using a cross-encoder to improve precision before passing to the generator.
4. **Generation:** A generative LLM receives the top-k chunks as context and generates a coherent answer. The prompt explicitly instructs the model to ground every claim in a specific retrieved passage.
5. **Citation Extraction:** The model outputs inline citations (passage ID, paper metadata). A post-processing step maps these back to exact quotes in the source chunks and formats the final response.
**Frameworks and tools:** LangChain or LlamaIndex for pipeline orchestration, FAISS or ChromaDB for vector storage, HuggingFace Transformers for encoders and re-rankers, arXiv / Semantic Scholar / PubMed Central / CORE APIs for multi-source paper retrieval.

---
## 5. Dataset
 
Since the system retrieves papers dynamically at query time, there is no single static training dataset. However, the following resources are relevant:
 
| Resource | Purpose | Source |
|---|---|---|
| **Natural Questions (NQ)** | Open-domain QA benchmark for evaluation | [https://ai.google.com/research/NaturalQuestions] |
| **QASPER** | QA dataset over scientific papers (NLP domain) | [https://allenai.org/data/qasper] |
| **SciFact** | Fact-checking dataset over scientific claims with evidence sentences | [https://github.com/allenai/scifact] |
| **Semantic Scholar Open Research Corpus (S2ORC)** | Large corpus of full-text scientific papers for offline indexing experiments | [https://github.com/allenai/s2orc] |

---
