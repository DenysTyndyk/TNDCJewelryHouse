import { Header, Footer } from '../components';
import { Outlet } from 'react-router-dom';
import ConsentBanner from '../components/ConsentBanner';
function AppLayout() {
    return (
        <div className="app-layout">
            <Header />
            <Outlet />
            <Footer />
            <ConsentBanner />
        </div>
    )
}
export default AppLayout;