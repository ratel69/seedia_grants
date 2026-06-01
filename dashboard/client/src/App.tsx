import { Switch, Route, Router } from "wouter";
import { useHashLocation } from "wouter/use-hash-location";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "@/lib/queryClient";
import { Toaster } from "@/components/ui/toaster";
import { ThemeProvider } from "@/components/ThemeProvider";
import { Sidebar } from "@/components/Sidebar";
import GrantsPage from "@/pages/GrantsPage";
import GrantDetailPage from "@/pages/GrantDetailPage";
import StatsPage from "@/pages/StatsPage";
import NotFound from "@/pages/not-found";

function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen bg-background overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-auto">
        {children}
      </main>
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <Router hook={useHashLocation}>
          <AppLayout>
            <Switch>
              <Route path="/" component={GrantsPage} />
              <Route path="/grants" component={GrantsPage} />
              <Route path="/grants/:id" component={GrantDetailPage} />
              <Route path="/stats" component={StatsPage} />
              <Route component={NotFound} />
            </Switch>
          </AppLayout>
        </Router>
        <Toaster />
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
