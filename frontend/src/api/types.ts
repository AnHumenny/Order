export interface Product {
  id: number;
  name: string;
  description: string;
  price: string;
  category: {
    id: number;
    name: string;
  };
}

export type Category = {
  id: number;
  name: string;
};

export interface User {
  username: string;
  token: string;
}

export interface AuthContextType {
  user: User | null;
  loginUser: (user: User) => void;
  logoutUser: () => void;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface Props {
  children: ReactNode;
}

export interface State {
  hasError: boolean;
}

export interface CartItem {
  id: number;
  product_id: number;
  name: string;
  price: number;
  quantity: number;
}

export interface CartContextType {
  cart: CartItem[];
  addToCart: (item: CartItem) => Promise<void>;
  fetchCart: () => Promise<void>;
  clearCart: () => Promise<void>;
  updateQuantity: (productId: number, action: 'increment' | 'decrement') => Promise<void>;
}

export interface UserBoxProps {
  user: {
    username: string;
    id?: number;
    email?: string;
  } | null;
  cart: CartItem[];
  onLogout: () => void;
}

interface OrderData {
  items: Array<{
    product_id: number;
    quantity: number;
    price: number;
  }>;
  total_amount: number;
}

interface CheckoutSessionResponse {
  id: string;
  url: string;
  session_id?: string;
  checkout_url?: string;
}
