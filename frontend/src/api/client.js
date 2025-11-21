import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000'
})

export const fetcher = async (url) => {
  const { data } = await api.get(url)
  return data
}

export const patchMovimiento = async (id, payload) => {
  const { data } = await api.patch(`/movimientos/${id}`, payload)
  return data
}

export const exportMovimientosCsv = async (params) => {
  const { data } = await api.get('/movimientos/export', {
    params,
    responseType: 'blob'
  })
  return data
}

export default api
