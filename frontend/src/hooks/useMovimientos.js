import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetcher } from '../api/client'

const serializeParams = (params = {}) => {
  const searchParams = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null || value === '') return
    if (Array.isArray(value)) {
      if (value.length) searchParams.set(key, value.join(','))
    } else {
      searchParams.set(key, value)
    }
  })
  const query = searchParams.toString()
  return { query, searchParams }
}

export function useMovimientos(params = {}) {
  const { query } = useMemo(() => serializeParams(params), [params])
  const key = useMemo(() => ['movimientos', query], [query])
  return useQuery({
    queryKey: key,
    queryFn: () => fetcher(`/movimientos${query ? `?${query}` : ''}`),
    keepPreviousData: true
  })
}

export { serializeParams }
