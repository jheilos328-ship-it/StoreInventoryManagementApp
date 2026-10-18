import RecommendationCard from "../components/RecommendationCard";
import LoadingBar from "../components/loadingbar";
import type { RecommendationAction } from "../services/api";

type RecommendationsPageProps = {
  actions: RecommendationAction[];
  error: string | null;
  isLoading: boolean;
  onBack: () => void;
  onRetry: () => void;
};

function RecommendationsPage({ actions, error, isLoading, onBack, onRetry }: RecommendationsPageProps) {
  return (
    <main className="recommendations-shell">
      <header className="recommendations-header">
        <div>
          <p className="product-label">Top Recommendations</p>
          <h1>Here are the 5 things to pay attention to.</h1>
        </div>
        <button className="secondary-button" type="button" onClick={onBack}>
          Back
        </button>
      </header>

      {isLoading && (
        <section className="analysis-loading" role="status" aria-live="polite">
          <p>Analyzing inventory...</p>
          <LoadingBar />
        </section>
      )}

      {!isLoading && error && (
        <section className="status-panel" role="alert">
          <p>{error}</p>
          <button className="primary-button compact" type="button" onClick={onRetry}>
            Try Again
          </button>
        </section>
      )}

      {!isLoading && !error && (
        <section className="recommendations-list" aria-label="Inventory recommendations">
          {actions.map((action, index) => (
            <RecommendationCard action={action} key={`${action.product}-${action.action_type}-${index}`} />
          ))}
          {actions.length === 0 && (
            <p className="status-message">No urgent inventory decisions found.</p>
          )}
        </section>
      )}
    </main>
  );
}

export default RecommendationsPage;
