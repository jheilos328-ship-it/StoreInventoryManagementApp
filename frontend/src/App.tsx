import { useState } from "react";
import LandingPage from "./pages/LandingPage";
import RecommendationsPage from "./pages/RecommendationsPage";
import { analyzeInventory, type RecommendationAction } from "./services/api";

type View = "landing" | "recommendations";

function App() {
  const [view, setView] = useState<View>("landing");
  const [actions, setActions] = useState<RecommendationAction[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleAnalyzeInventory() {
    setView("recommendations");
    setIsLoading(true);
    setError(null);

    try {
      const nextActions = await analyzeInventory();
      setActions(nextActions.slice(0, 5));
    } catch {
      setActions([]);
      setError("Unable to analyze inventory. Please try again.");
    } finally {
      setIsLoading(false);
    }
  }

  if (view === "recommendations") {
    return (
      <RecommendationsPage
        actions={actions}
        error={error}
        isLoading={isLoading}
        onBack={() => setView("landing")}
        onRetry={handleAnalyzeInventory}
      />
    );
  }

  return <LandingPage onAnalyze={handleAnalyzeInventory} isLoading={isLoading} />;
}

export default App;
