import { ingressApi } from './ingress'

interface LoginResponse {
  access_token: string
  token_type: string
}

interface RegisterResponse {
  id: number
  email: string
}

export function login(email: string, password: string) {
  return ingressApi.post<LoginResponse>('/auth/login', { email, password })
}

export function register(email: string, password: string) {
  return ingressApi.post<RegisterResponse>('/auth/register', { email, password })
}
