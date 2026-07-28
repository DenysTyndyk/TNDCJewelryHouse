import { Header, Footer } from '../components';
import { Outlet } from 'react-router-dom';
function AppLayout() {
    return (
        <div>
            <Header />
            <Outlet />
            <Footer />
        </div>
    )
}
export default AppLayout;