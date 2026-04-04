import React from 'react';
import Layout from './components/Layout';
import Dashboard from './components/Dashboard';
import CallLogs from './components/CallLogs';
import CallDetails from './components/CallDetails';
import Escalations from './components/Escalations';

export default function App() {
  const [activeTab, setActiveTab] = React.useState('dashboard');
  const [selectedCallId, setSelectedCallId] = React.useState<string | null>(null);

  const handleSelectCall = (id: string) => {
    setSelectedCallId(id);
    setActiveTab('call-details');
  };

  const renderContent = () => {
    if (activeTab === 'call-details' && selectedCallId) {
      return <CallDetails callId={selectedCallId} onBack={() => setActiveTab('call-logs')} />;
    }

    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />;
      case 'call-logs':
        return <CallLogs onSelectCall={handleSelectCall} />;
      case 'escalations':
        return <Escalations />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <Layout activeTab={activeTab === 'call-details' ? 'call-logs' : activeTab} setActiveTab={setActiveTab}>
      {renderContent()}
    </Layout>
  );
}
