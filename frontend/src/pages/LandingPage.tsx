type LandingPageProps = {
  isLoading: boolean;
  onAnalyze: () => void;
};

function LandingPage({ isLoading, onAnalyze }: LandingPageProps) {
  return (
    <main className="landing-shell">
      <section className="landing-panel" aria-labelledby="landing-title">
        <p className="product-label">Inventory Decision Engine</p>
        <h1 id="landing-title">Your inventory. Prioritized.</h1>
        <p className="landing-subheadline">
          Turn store inventory data into the 5 decisions that matter most.
        </p>
        <button className="primary-button" type="button" onClick={onAnalyze} disabled={isLoading}>
          {isLoading ? "Analyzing..." : "Analyze Sample Inventory"}
        </button>
      </section>
    </main>
  );
}

export default LandingPage;
