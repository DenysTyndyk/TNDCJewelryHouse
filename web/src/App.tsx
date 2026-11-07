import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Home, Categories, Contact, Cart, About , AppLayout, Login,Register,Account, VerifyEmail, ForgotPassword, ResetPassword} from './pages'
import {CartProvider,AuthProvider,LanguageProvider} from './context'
function App() {
  return (
    <LanguageProvider>
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
        <Route path="/verify-email" element={<VerifyEmail />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />
        </Route>
      </Routes>
    </BrowserRouter>
        </CartProvider>
    </AuthProvider>
    </LanguageProvider>
  )
}

export default App