from DeepSeekClient import DeepSeekClient

# Tested!
class QueryProcessor:
    def __init__(self, query: str, model):
        self.query = query
        self.multi_queries = None
        self.model = model
        self.deepseek_client = DeepSeekClient()

    def query_processing(self):
        prompt = f"""
        Given the following question, generate a list of keywords that could be used to retrieve information from a database of articles.
        The retrieved information will be used to answer the original question.
        Stay relevant to the question itself.

        The question to create queries based off of is:
        {self.query}

        Return the output as a list of 3 queries only with no punctuation or numbering. Just have the questions in separate lines.
        Example Query: "What is the latest news on climate change?"
        Example Output: climate change latest news
        Example Query: "Who won the best actor Oscar in 2023?"
        Example Output: best actor Oscar 2023
        """
        response = self.deepseek_client.chat(
            messages=[
                {"role": "system", "content": "You are an expert in breaking down queries into search terms."},
                {"role": "user", "content": prompt}
            ]
        )
        output = response["message"]["content"]
        self.multi_queries = output.split('\n')
        if len(self.multi_queries) > 3:
            self.multi_queries = self.multi_queries[:3]
            
        return self.multi_queries