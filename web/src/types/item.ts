export type Item = {
    id: number;
    slug?: string;
    title: string;
    price: number;
    currency?: string;
    description: string;
    category: string;
    images: string[];
    quantity?: number; 
}
