import { useState } from "react";
import type { RecommendationAction } from "../services/api";

type RecommendationCardProps = {
  action: RecommendationAction;
};

const priorityLabels: Record<RecommendationAction["priority"], string> = {
  high: "High Priority",
  medium: "Medium Priority",
  low: "Low Priority",
};

function formatActionType(value: string) {
  return value.replace(/_/g, " ").toUpperCase();
}

function formatMoney(value: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}

function formatTrend(value: number) {
  const percentage = Math.round(value * 100);
  return `${percentage > 0 ? "+" : ""}${percentage}%`;
}

function RecommendationCard({ action }: RecommendationCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <article className="recommendation-card">
      <div className="card-topline">
        <span className={`priority-badge ${action.priority}`}>{priorityLabels[action.priority]}</span>
        <span className="confidence-pill">{action.confidence} confidence</span>
      </div>

      <div className="card-main">
        <p className="product-name">{action.product}</p>
        <p className="action-type">{formatActionType(action.action_type)}</p>
        <h2>{action.action}</h2>
        <p className="why-text">{action.why}</p>
      </div>

      <button className="details-button" type="button" onClick={() => setIsExpanded((value) => !value)}>
        {isExpanded ? "Hide Details" : "View Details"}
      </button>

      {isExpanded && (
        <dl className="metrics-grid">
          <div>
            <dt>Velocity</dt>
            <dd>{action.metrics.velocity.toFixed(1)}/day</dd>
          </div>
          <div>
            <dt>Days of Stock</dt>
            <dd>{action.metrics.days_of_stock.toFixed(1)}</dd>
          </div>
          <div>
            <dt>Revenue/day</dt>
            <dd>{formatMoney(action.metrics.revenue_per_day)}</dd>
          </div>
          <div>
            <dt>Trend</dt>
            <dd>{formatTrend(action.metrics.trend)}</dd>
          </div>
          <div>
            <dt>Confidence</dt>
            <dd>{action.confidence}</dd>
          </div>
        </dl>
      )}
    </article>
  );
}

export default RecommendationCard;
