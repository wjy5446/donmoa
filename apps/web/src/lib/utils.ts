import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * 금액 포맷팅
 */
export function formatMoney(amountMinor: string | bigint, currency: string): string {
  const scales: Record<string, number> = {
    KRW: 1,
    USD: 100,
    EUR: 100,
    JPY: 1,
  }

  const scale = scales[currency] || 100
  const amount = Number(amountMinor) / scale

  return new Intl.NumberFormat('ko-KR', {
    style: 'currency',
    currency,
  }).format(amount)
}

/**
 * 수량 포맷팅
 */
export function formatQuantity(qtyNano: string | bigint): string {
  const qty = Number(qtyNano) / 1_000_000_000
  return qty.toLocaleString('ko-KR', { maximumFractionDigits: 8 })
}

/**
 * 날짜 포맷팅
 */
export function formatDate(date: string | Date): string {
  return new Date(date).toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

/**
 * 퍼센트 포맷팅
 */
export function formatPercent(value: number): string {
  return `${(value * 100).toFixed(2)}%`
}

