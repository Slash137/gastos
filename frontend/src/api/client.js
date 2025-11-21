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

export const analyzeImport = async (file) => {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await api.post('/import/analyze', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return data
}

export const previewImport = async (file, mapping, options) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('payload', JSON.stringify({ mapping, options }))
  const { data } = await api.post('/import/preview', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return data
}

export const applyImport = async (file, mapping, options) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('payload', JSON.stringify({ mapping, options }))
  const { data } = await api.post('/import/apply', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return data
}

export default api
