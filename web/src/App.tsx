import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Home, Categories, Contact, Cart, About , AppLayout, Login,Register,Account} from './pages'
import {CartProvider,AuthProvider} from './context'
function App() {
  return (
    <AuthProvider>
        <CartProvider>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AppLayout />}>
        <Route index element={<Home />} />
        <Route path="/categories" element={<Categories />} />
        <Route path="/cart" element={<Cart />} />
        <Route path="/about" element={<About />} />
        <Route path="/contact" element={<Contact />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/account" element={<Account />} />
        </Route>
      </Routes>
    </BrowserRouter>
        </CartProvider>
    </AuthProvider>
  )
}

export default App