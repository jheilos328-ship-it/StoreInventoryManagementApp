export type RecommendationMetrics = {
  velocity: number;
  days_of_stock: number;
  revenue_per_day: number;
  trend: number;
};

export type RecommendationAction = {
  product: string;
  action_type: string;
  action: string;
  why: string;
  priority: "high" | "medium" | "low";
  confidence: "high" | "medium" | "low";
  metrics: RecommendationMetrics;
};

type AnalyzeResponse = {
  actions: RecommendationAction[];
};

const API_URL = "/analyze";

const mockInventory = [
  {
    product_id: "tee-blue",
    name: "Blue T-Shirt",
    stock: 7,
    cost: 8,
    price: 28,
    sales_history: [2, 3, 4, 4, 5, 4, 6, 4, 5, 5, 4, 6, 5, 5],
  },
  {
    product_id: "mug-white",
    name: "White Ceramic Mug",
    stock: 180,
    cost: 3,
    price: 12,
    sales_history: [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  },
  {
    product_id: "cap-black",
    name: "Black Cap",
    stock: 12,
    cost: 5,
    price: 24,
    sales_history: [1, 1, 1, 2, 2, 2, 2, 3, 3, 4, 4, 4, 5, 5],
  },
  {
    product_id: "socks-gray",
    name: "Gray Socks",
    stock: 260,
    cost: 2,
    price: 9,
    sales_history: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  },
];

export async function analyzeInventory(): Promise<RecommendationAction[]> {
  const response = await fetch(API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ inventory: mockInventory }),
  });

  if (!response.ok) {
    throw new Error("Analyze request failed");
  }

  const data = (await response.json()) as AnalyzeResponse;
  return Array.isArray(data.actions) ? data.actions : [];
}
