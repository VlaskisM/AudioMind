import axios from 'axios'

export const ingressApi = axios.create({
  baseURL: '/api/ingress',
})
