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
