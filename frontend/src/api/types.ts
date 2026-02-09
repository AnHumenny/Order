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
  children: JSX.Element;
}

export interface CartItem {
  id: number;
  name: string;
  price: number;
  quantity: number;
}

export interface CartContextType {
  cart: CartItem[];
  addToCart: (item: CartItem) => Promise<void>;
  fetchCart: () => Promise<void>;
}
