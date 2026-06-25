export interface Product {
  id: string
  title: string
  price: number
  original_price: number | null
  discount_percentage: number | null
  free_shipping: number | null
  condition: string | null
  installments: string | null
  currency_id: string
  permalink: string
  thumbnail: string
  first_seen: string
  last_seen: string
}
