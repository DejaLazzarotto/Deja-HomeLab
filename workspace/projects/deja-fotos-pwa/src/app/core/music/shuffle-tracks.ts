export function shuffleTracks<T>(
  tracks: readonly T[],
  random: () => number = Math.random,
): T[] {
  const result = [...tracks];

  for (let index = result.length - 1; index > 0; index--) {
    const selected = Math.floor(random() * (index + 1));

    [result[index], result[selected]] = [
      result[selected],
      result[index],
    ];
  }

  return result;
}
