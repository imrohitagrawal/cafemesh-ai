# Retrieval strategy: structured facts now, RAG when documents justify it

## Current implementation

The demo uses deterministic lexical retrieval over a small, versioned synthetic menu catalog. It recognizes explicit drink concepts and aliases, narrows by exact menu names where possible, then applies price, availability, temperature, diet, allergy, cross-contact, and visit-time rules in backend code. Each candidate carries a menu source ID and inventory/queue evidence labels. The ADK tools separately read structured menu, visit, and owner facts. This is tool-grounded retrieval, but it is **not a RAG pipeline**: there is no document ingestion, chunking, embedding model, vector index, semantic reranker, or citation evaluator.

## Why full RAG is not needed for the demo menu

Prices, ingredients, allergens, cross-contact status, stock, opening state, queue, and seating are structured, changing business facts. A vector search over prose is a poor authority for these values and can retrieve stale or approximate statements. A concise structured catalog and deterministic filters are faster, inspectable, and easier to test. Natural-language matching currently uses a small lexical synonym map; it is not semantic search and can miss paraphrases.

## When to add RAG

Add a scoped, read-only RAG layer when participating cafés provide enough long-form material to justify it: preparation procedures, equipment notes, ingredient provenance documents, accessibility descriptions, café policies, or curated neighborhood guides. Keep canonical prices, availability, allergen decisions, inventory, and confirmed bookings in structured services. RAG may explain a verified fact or retrieve relevant procedure text; it must not override authoritative records or authorize an action.

## RAG release gates

1. Define approved document sources, tenant/location ACLs, owners, freshness rules, and deletion propagation.
2. Parse, chunk, and index versioned records with document ID, chunk ID, location, effective dates, and source timestamp.
3. Use hybrid exact/semantic retrieval with an explicit no-result threshold; filter by tenant before retrieval and reranking.
4. Require citations that resolve to the exact retrieved chunks. Preserve unknown and conflicting evidence.
5. Add reviewed retrieval goldens for paraphrases, stale/contradictory content, prompt injection in documents, cross-tenant retrieval, no-answer cases, and citation support.
6. Measure retrieval recall and citation correctness separately from answer quality. Run deterministic safety tests first; optionally calibrate an LLM judge against human labels before using it as a non-blocking quality signal.
7. Keep action authorization, allergy policy, price, stock, and order confirmation in deterministic services.

The current `evals/menu-retrieval-goldens.json` covers deterministic catalog selection, an unsupported smoothie query, and the canonical peanut-allergy request. It is a small regression set, not a broad semantic retrieval benchmark and not an LLM-as-judge pipeline.
