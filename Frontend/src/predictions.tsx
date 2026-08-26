import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import "./Predictions.css";

type PredictionResponse = {
	idfg: number;
	prediction: {
		bsr: number;
		wraa: number;
		rlr: number;
	};
};

const API_URL =
	import.meta.env.VITE_PREDICTION_API_URL ?? "http://localhost:8001";

export default function Predictions() {
	const { id } = useParams();
	const nav = useNavigate();

	const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState("");

	useEffect(() => {
		if (!id) return;

		const controller = new AbortController();

		async function getPrediction() {
			setLoading(true);
			setError("");
			setPrediction(null);

			try {
				const response = await fetch(`${API_URL}/prediction/${id}`, {
					signal: controller.signal,
				});

				if (!response.ok) {
					const body = await response.json().catch(() => null);
					const detail = body?.detail;

					if (response.status === 404) {
						throw new Error(
							detail ?? `No prediction data found for player ${id}.`,
						);
					}

					throw new Error(
						detail ?? `Prediction request failed (${response.status})`,
					);
				}

				setPrediction(await response.json());
			} catch (requestError) {
				if (requestError instanceof DOMException && requestError.name === "AbortError") {
					return;
				}
				setError(
					requestError instanceof Error
						? requestError.message
						: "Unable to retrieve a prediction.",
				);
			} finally {
				setLoading(false);
			}
		}

		getPrediction();

		return () => controller.abort();
	}, [id]);

	return (
		<main className="Predictions">
			<div className="predictions-top">
				<button className="back-btn" onClick={() => nav(`/players/${id}`)}>
					Back
				</button>
			</div>

			<h1>Predictions</h1>

			{loading && <p>Predicting…</p>}
			{error && <p role="alert">{error}</p>}

			{prediction && (
				<section aria-live="polite" className="prediction-result">
					<h2>Result</h2>
					<div className="prediction-stats">
						<div className="stat">
							<span className="stat-label">BSR</span>
							<span className="stat-value">{prediction.prediction.bsr.toFixed(2)}</span>
						</div>
						<div className="stat">
							<span className="stat-label">wRAA</span>
							<span className="stat-value">{prediction.prediction.wraa.toFixed(2)}</span>
						</div>
						<div className="stat">
							<span className="stat-label">RLR</span>
							<span className="stat-value">{prediction.prediction.rlr.toFixed(2)}</span>
						</div>
					</div>
				</section>
			)}
		</main>
	);
}