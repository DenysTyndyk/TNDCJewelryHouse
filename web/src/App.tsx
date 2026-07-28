import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Home, Categories, Contact, Cart, About , AppLayout} from './pages'
import {CartProvider} from './context/cartContext'
function App() {
  return (
        <CartProvider>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AppLayout />}>
        <Route index element={<Home />} />
        <Route path="/categories" element={<Categories />} />
        <Route path="/cart" element={<Cart />} />
        <Route path="/about" element={<About />} />
        <Route path="/contact" element={<Contact />} />
        </Route>
      </Routes>
    </BrowserRouter>
        </CartProvider>
  )
}

export default App