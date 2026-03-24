import axios from 'axios'

export const analysisApi = axios.create({
  baseURL: '/api/analysis',
})
