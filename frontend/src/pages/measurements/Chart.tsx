import { useXScale, useYScale } from "@mui/x-charts/hooks";
import { LineChart } from "@mui/x-charts/LineChart";
import type { MeasurementRead, SeriesRead } from "@/client";

interface MeasurementsChartProps {
	measurements: MeasurementRead[];
	series: SeriesRead[];
	selected?: MeasurementRead;
}

// A ring around the measurement picked in the table.
const SelectedPoint = ({
	measurement,
	color,
}: {
	measurement: MeasurementRead;
	color: string;
}) => {
	const xScale = useXScale<"time">();
	const yScale = useYScale<"linear">(String(measurement.seriesId));
	return (
		<circle
			cx={xScale(new Date(measurement.timestamp))}
			cy={yScale(measurement.value)}
			r={9}
			fill="none"
			stroke={color}
			strokeWidth={3}
		/>
	);
};

// One line per series. All lines share one time axis, so each series gets a
// value (or null) for every timestamp; each series has its own y axis (units differ).
const MeasurementsChart = ({
	measurements,
	series,
	selected,
}: MeasurementsChartProps) => {
	// The API returns ISO timestamps in one format, so string sort == time sort.
	const times = [...new Set(measurements.map((m) => m.timestamp))].sort();
	const timeIndex = new Map(times.map((time, i) => [time, i]));
	const values = new Map(
		series.map((s) => [s.id, times.map((): number | null => null)]),
	);
	for (const m of measurements) {
		const line = values.get(m.seriesId);
		if (line) line[timeIndex.get(m.timestamp) as number] = m.value;
	}
	const shown = measurements.some((m) => m.id === selected?.id);
	const selectedSeries = series.find((s) => s.id === selected?.seriesId);

	return (
		<LineChart
			height={350}
			xAxis={[
				{
					scaleType: "time",
					data: times.map((time) => new Date(time)),
					valueFormatter: (date: Date) => date.toLocaleString(),
				},
			]}
			yAxis={series.map((s, i) => ({
				id: String(s.id),
				label: s.unit,
				position: i % 2 ? "right" : "left",
			}))}
			series={series.map((s) => ({
				id: String(s.id),
				yAxisId: String(s.id),
				label: `${s.name} (${s.unit})`,
				color: s.color,
				data: values.get(s.id) ?? [],
				connectNulls: true,
				valueFormatter: (value) =>
					value === null ? null : `${value} ${s.unit}`,
				showMark: true,
			}))}
		>
			{selected && shown && selectedSeries && (
				<SelectedPoint measurement={selected} color={selectedSeries.color} />
			)}
		</LineChart>
	);
};

export default MeasurementsChart;
