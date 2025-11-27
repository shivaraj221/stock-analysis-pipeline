# tools/news_orchestrator.py
from crewai.tools import BaseTool
from tools.news_fetcher import NewsFetcherTool
from tools.news_summarizer import NewsSummarizerTool

class NewsOrchestratorTool(BaseTool):
    name: str = "news_orchestrator_tool"
    description: str = "Orchestrates the complete news pipeline: fetch news, then inject context"

    def _run(self) -> str:
        results = []
        
        # Step 1: Fetch news
        print("\n" + "="*60)
        print("STEP 1: FETCHING NEWS")
        print("="*60)
        fetcher = NewsFetcherTool()
        fetch_result = fetcher._run()
        results.append(fetch_result)
        print(fetch_result)
        
        # Step 2: Inject context
        print("\n" + "="*60)
        print("STEP 2: INJECTING NEWS CONTEXT")
        print("="*60)
        summarizer = NewsSummarizerTool()
        summary_result = summarizer._run()
        results.append(summary_result)
        print(summary_result)
        
        return "\n\n".join(results)

if __name__ == "__main__":
    tool = NewsOrchestratorTool()
    print(tool._run())