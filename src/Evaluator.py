from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import concurrent.futures
from util import cosine_similarity
from DrafterAgent import DrafterAgent

class Evaluator:
    def __init__(self, ranked_chunks, query_embedding, model):
        self.chunks = ranked_chunks
        self.query = query_embedding
        self.model = model
        self.chunk_answer_similarity = 0
        self.chunk_query_similarity = 0
        self.query_answer_similarity = 0

    def evaluate(self, answer, answer_embedding):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            chunk_query_future = executor.submit(cosine_similarity, self.chunks[0]["embedding"], self.query)
            chunk_answer_future = executor.submit(cosine_similarity, self.chunks[0]["embedding"], answer_embedding)
            query_answer_future = executor.submit(cosine_similarity, self.query, answer_embedding)
            faithfulness_future = executor.submit(self.faithfulness, answer)

            self.chunk_query_similarity = chunk_query_future.result()
            chunk_answer_similarity = chunk_answer_future.result()
            self.query_answer_similarity = query_answer_future.result()
            faithfulness_score = faithfulness_future.result()

        if faithfulness_score >= chunk_answer_similarity:
            self.chunk_answer_similarity = faithfulness_score
        else:
            self.chunk_answer_similarity = chunk_answer_similarity

        average = (self.chunk_answer_similarity + self.chunk_query_similarity + self.query_answer_similarity) / 3

        return average

    def faithfulness(self, answer):
        # prompt = f"""You are an expert evaluator. You can take an input and return all claims made in the answer.
        
        # Input:
        # {answer}
        
        # Expected Output Format: ["claim 1", "claim 2", "..."]
        # """
        # response = self.client.chat.completions.create(
        #     model="medical-device-research-model",
        #     messages=[
        #         {"role": "user", "content": prompt}
        #     ]
        # )

        # claims = response.choices[0].message.content.strip()

        # prompt = f"""You are an expert evaluator. Given the following claims and context chunks, determine the number of claims that are fully supported by the context.
        # - Go one claim at a time and check if it is supported by at least one of the context chunks.
        # - If a claim is supported by any chunk, count that as a supported claim.

        # Claims:
        # {claims}

        # Context Chunks:
        # {self.chunks}

        # Expected Output: an integer representing the number of fully supported claims.
        # """
        # response = self.client.chat.completions.create(
        #     model="medical-device-research-model",
        #     messages=[
        #         {"role": "user", "content": prompt}
        #     ]
        # )

        # try:
        #     return float(response.choices[0].message.content.strip())/len(claims.strip('[]').split(','))
        # except Exception as e:
        #     return 0.0
        return 0.0

    def drafting(self, answer):
        Agent = DrafterAgent(self.chunks, self.query, answer, self.model)
        assessment = Agent.assess()
        return Agent.draft(assessment)

    def format_evaluation_results(self):
        if not self.chunk_query_similarity and not self.chunk_answer_similarity and not self.query_answer_similarity:
            return ""
        
        formatted_text = "\n\n---\n**Evaluation Scores:**\n\n"

        if self.chunk_answer_similarity >= 0.8:
            formatted_text += f"**Grounded in source:** 🟢 Excellent - {self.chunk_answer_similarity:.3f}\n"
        elif self.chunk_answer_similarity >= 0.5:
            formatted_text += f"**Grounded in source:** 🟡 Good - {self.chunk_answer_similarity:.3f}\n"
        elif self.chunk_answer_similarity >= 0.3:
            formatted_text += f"**Grounded in source:** 🟠 Fair - {self.chunk_answer_similarity:.3f}\n"
        else:
            formatted_text += f"**Grounded in source:** 🔴 Poor - {self.chunk_answer_similarity:.3f}\n"

        if self.chunk_query_similarity >= 0.8:
            formatted_text += f"**Relevance to query:** 🟢 Excellent - {self.chunk_query_similarity:.3f}\n"
        elif self.chunk_query_similarity >= 0.5:
            formatted_text += f"**Relevance to query:** 🟡 Good - {self.chunk_query_similarity:.3f}\n"
        elif self.chunk_query_similarity >= 0.3:
            formatted_text += f"**Relevance to query:** 🟠 Fair - {self.chunk_query_similarity:.3f}\n"
        else:
            formatted_text += f"**Relevance to query:** 🔴 Poor - {self.chunk_query_similarity:.3f}\n"

        if self.query_answer_similarity >= 0.8:
            formatted_text += f"**Answer Quality:** 🟢 Excellent - {self.query_answer_similarity:.3f}\n"
        elif self.query_answer_similarity >= 0.5:
            formatted_text += f"**Answer Quality:** 🟡 Good - {self.query_answer_similarity:.3f}\n"
        elif self.query_answer_similarity >= 0.3:
            formatted_text += f"**Answer Quality:** 🟠 Fair - {self.query_answer_similarity:.3f}\n"
        else:
            formatted_text += f"**Answer Quality:** 🔴 Poor - {self.query_answer_similarity:.3f}\n"

        return formatted_text