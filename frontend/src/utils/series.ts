import type { SeriesRead } from "@/client";

// "Temperature (°C)", or just the name when the series has no unit.
export const seriesLabel = (series: Pick<SeriesRead, "name" | "unit">) =>
	series.unit ? `${series.name} (${series.unit})` : series.name;
