import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000'
})

export const fetcher = async (url) => {
  const { data } = await api.get(url)
  return data
}

export default api
