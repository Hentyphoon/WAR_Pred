// Non-zero values that would round to 0.00 (or -0.00) show their sign instead.
export function formatStat(value: number): string {
	if (value !== 0 && Math.abs(value) < 0.005) {
		return value > 0 ? "<0.01" : ">-0.01";
	}
	return value.toFixed(2);
}
