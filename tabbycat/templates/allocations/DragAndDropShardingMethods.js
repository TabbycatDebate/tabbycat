
export function splitDebates (debates, desiredSplit) {
  const splitDebates = []
  let n = desiredSplit
  let size = Math.floor(debates.length / n)
  let i = 0

  // Sort debates into even chunks
  if (debates.length % n === 0) {
    while (i < debates.length) {
      splitDebates.push(debates.slice(i, i += size))
    }
  } else {
    n -= 1
    if (debates.length % size === 0) {
      size -= 1
    }
    while (i < size * n) {
      splitDebates.push(debates.slice(i, i += size))
    }
    splitDebates.push(debates.slice(size * n))
  }
  return splitDebates
}

export function sortInterleaved (debates, desiredSplit) {
  const interleavedDebates = []
  let j = 0
  let i

  // Make multidimensional array for each shard
  for (j = 0; j < desiredSplit; j += 1) {
    interleavedDebates[j] = []
  }

  // Split big array equally into shards; evenly distributing large-small
  j = 0
  for (i = 0; i < debates.length; i += 1) {
    interleavedDebates[j].push(debates[i])
    j += 1
    if (j >= desiredSplit) {
      j = 0
    }
  }

  return interleavedDebates.flat()
}
