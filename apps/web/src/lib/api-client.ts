/**
 * API 클라이언트
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001'

export class ApiClient {
  private baseUrl: string
  private accessToken?: string

  constructor(baseUrl: string = API_URL) {
    this.baseUrl = baseUrl
  }

  setAccessToken(token: string) {
    this.accessToken = token
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    }

    if (this.accessToken) {
      headers['Authorization'] = `Bearer ${this.accessToken}`
    }

    const response = await fetch(url, {
      ...options,
      headers,
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        error: { message: 'An error occurred' },
      }))
      throw new Error(error.error?.message || 'Request failed')
    }

    return response.json()
  }

  // Snapshot API
  async getSnapshots(params?: { from?: string; to?: string; limit?: number }) {
    const query = new URLSearchParams(params as any).toString()
    return this.request(`/v1/snapshots${query ? `?${query}` : ''}`)
  }

  async getSnapshot(id: number) {
    return this.request(`/v1/snapshots/${id}`)
  }

  async commitSnapshot(data: any) {
    return this.request('/v1/snapshots/commit', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  // Dashboard API
  async getDashboardSummary(date: string) {
    return this.request(`/v1/dashboard/summary?date=${date}`)
  }

  async getTimeseries(params: {
    metric: string
    interval?: string
    from?: string
    to?: string
  }) {
    const query = new URLSearchParams(params as any).toString()
    return this.request(`/v1/dashboard/timeseries?${query}`)
  }

  async getAllocations(date: string, group: string) {
    return this.request(`/v1/dashboard/allocations?date=${date}&group=${group}`)
  }

  // Portfolio API
  async getAccounts() {
    return this.request('/v1/accounts')
  }

  // Market Data API
  async searchInstruments(query: string) {
    return this.request(`/v1/instruments?query=${encodeURIComponent(query)}`)
  }

  // Rebalancing API
  async getRebalanceTargets() {
    return this.request('/v1/rebalance/targets')
  }

  async saveRebalanceTargets(targets: any[]) {
    return this.request('/v1/rebalance/targets', {
      method: 'POST',
      body: JSON.stringify({ targets }),
    })
  }

  async createRebalanceSuggestion(data: any) {
    return this.request('/v1/rebalance/suggest', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }
}

export const apiClient = new ApiClient()

