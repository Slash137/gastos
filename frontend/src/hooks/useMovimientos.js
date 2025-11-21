import { useQuery } from '@tanstack/react-query'
import { fetcher } from '../api/client'

export function useMovimientos(params = {}) {
  const query = new URLSearchParams(params).toString()
  const key = ['movimientos', query]
  return useQuery({ queryKey: key, queryFn: () => fetcher(`/movimientos${query ? `?${query}` : ''}`) })
}
