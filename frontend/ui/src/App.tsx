import React, { useState, useEffect, useCallback } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import axios from 'axios';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);
import highlight from 'highlight.js';
import 'highlight.js/styles/github.css';

// Types
interface Requirement {
  session_id: string;
  requirement_id: string;
  title: string;
  actor: string;
  goal: string;
  ac_count: number;
  status: string;
}

interface TestCase {
  id: string;
  title: string;
  type: string;
  priority: string;
  trace_to: string[];
}

interface TestSuite {
  session_id: string;
  test_count: number;
  coverage: any;
  test_cases: TestCase[];
  duplicates: any[];
}

interface RunStatus {
  id: string;
  status: string;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  output?: string;
  errors?: string;
  exit_code?: number;
}

interface Metrics {
  total_requirements: number;
  total_runs: number;
  pass_rate: number;
  recent_runs: any[];
  test_types: any;
  history: any[];
}

// Dashboard Component
const Dashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMetrics = async (isInitialLoad = false) => {
      try {
        const response = await axios.get('http://localhost:8080/api/metrics');
        setMetrics(response.data);
      } catch (error) {
        console.error('Failed to fetch metrics:', error);
      } finally {
        if (isInitialLoad) {
          setLoading(false);
        }
      }
    };

    fetchMetrics(true); // Initial load
    const interval = setInterval(() => fetchMetrics(false), 30000); // Background refresh
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="p-6">Loading dashboard...</div>;

  if (!metrics) return <div className="p-6 text-red-600">Failed to load metrics</div>;

  const chartData = {
    labels: metrics.history.slice(-10).map((h: any) => new Date(h.created_at).toLocaleDateString()),
    datasets: [{
      label: 'Test Runs',
      data: metrics.history.slice(-10).map((h: any) => h.status === 'completed' ? 1 : 0),
      borderColor: 'rgb(75, 192, 192)',
      backgroundColor: 'rgba(75, 192, 192, 0.2)',
      tension: 0.1
    }]
  };

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Dashboard</h1>
      
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-700">Total Requirements</h3>
          <p className="text-3xl font-bold text-blue-600">{metrics.total_requirements}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-700">Total Runs</h3>
          <p className="text-3xl font-bold text-green-600">{metrics.total_runs}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-700">Pass Rate</h3>
          <p className="text-3xl font-bold text-purple-600">{metrics.pass_rate.toFixed(1)}%</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-700">UI Real Mode</h3>
          <p className="text-3xl font-bold text-orange-600">{metrics.test_types.ui_real}</p>
        </div>
      </div>

      {/* Chart */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Test Run Trends</h3>
        <div className="h-64">
          <Line data={chartData} options={{ responsive: true, maintainAspectRatio: false }} />
        </div>
      </div>

      {/* Recent Runs */}
      <div className="bg-white p-6 rounded-lg shadow mt-6">
        <h3 className="text-lg font-semibold mb-4">Recent Test Runs</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left p-2">ID</th>
                <th className="text-left p-2">Status</th>
                <th className="text-left p-2">Created</th>
              </tr>
            </thead>
            <tbody>
              {metrics.recent_runs.map((run: any) => (
                <tr key={run.id} className="border-b">
                  <td className="p-2 font-mono text-sm">{run.id.slice(0, 8)}...</td>
                  <td className="p-2">
                    <span className={`px-2 py-1 rounded text-xs ${
                      run.status === 'completed' ? 'bg-green-100 text-green-800' :
                      run.status === 'failed' ? 'bg-red-100 text-red-800' :
                      'bg-yellow-100 text-yellow-800'
                    }`}>
                      {run.status}
                    </span>
                  </td>
                  <td className="p-2 text-sm">{new Date(run.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

// Test Generation Component
const TestGeneration: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'text' | 'file'>('text');
  const [storyText, setStoryText] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [allowDuplicates, setAllowDuplicates] = useState(false);
  const [currentStep, setCurrentStep] = useState<'input' | 'parsing' | 'parsed' | 'generating' | 'approving' | 'synthesizing' | 'running'>('input');
  
  const [requirement, setRequirement] = useState<Requirement | null>(null);
  const [testSuite, setTestSuite] = useState<TestSuite | null>(null);
  const [selectedTests, setSelectedTests] = useState<string[]>([]);
  const [runStatus, setRunStatus] = useState<RunStatus | null>(null);
  const [uiMode, setUiMode] = useState('real');
  const [apiMode, setApiMode] = useState('mock');
  const [autoPR, setAutoPR] = useState(false);
  const [autoGenerateCode, setAutoGenerateCode] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Step 1: Parse requirement
  const handleParse = async () => {
    if (!storyText.trim() && !file) {
      setError('Please enter text or upload a file');
      return;
    }

    setCurrentStep('parsing');
    setError(null);
    setSuccess(null);

    try {
      let response;
      if (activeTab === 'text') {
        response = await axios.post('http://localhost:8080/api/requirements', {
          story_text: storyText,
          domain: 'ecommerce',
          tags: ['poc']
        });
      } else if (file) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('domain', 'ecommerce');
        formData.append('tags', 'poc');
        response = await axios.post('http://localhost:8080/api/requirements/file', formData);
      }

              setRequirement(response.data);
        setCurrentStep('parsed');
        setSuccess('Requirement parsed successfully! View the parsed details below.');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to parse requirement');
      setCurrentStep('input');
    }
  };

  // Step 2: Generate tests
  const handleGenerate = async () => {
    if (!requirement) return;

    setCurrentStep('generating');
    setError(null);

    try {
      const response = await axios.post(`http://localhost:8080/api/requirements/${requirement.session_id}/generate`, {
        requirement_id: requirement.requirement_id,
        coverage: 'comprehensive',
        allow_duplicates: allowDuplicates
      });

      setTestSuite(response.data);
      setCurrentStep('approving');
      setSuccess('Tests generated successfully!');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate tests');
      setCurrentStep('generating');
    }
  };

  // Step 3: Approve tests
  const handleApprove = async () => {
    if (!requirement || !testSuite || selectedTests.length === 0) {
      setError('Please select tests to approve');
      return;
    }

    setCurrentStep('approving');
    setError(null);

    try {
      const response = await axios.post(`http://localhost:8080/api/requirements/${requirement.session_id}/approve`, {
        requirement_id: requirement.requirement_id,
        test_case_ids: selectedTests,
        approved: true,
        allow_duplicates: allowDuplicates
      });

      setCurrentStep('synthesizing');
      setSuccess('Tests approved! Code generated.');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to approve tests');
      setCurrentStep('approving');
    }
  };

  // Step 4: Run tests
  const handleRun = async () => {
    if (!requirement) return;

    setCurrentStep('running');
    setError(null);

    try {
      const response = await axios.post('http://localhost:8080/api/runs', {
        session_id: requirement.session_id,
      ui_mode: uiMode,
      api_mode: apiMode,
        auto_pr: autoPR
      });

      setRunStatus(response.data);
      setSuccess('Tests started! Check status below.');
      setCurrentStep('input'); // Reset to start
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to start tests');
      setCurrentStep('synthesizing');
    }
  };

  const handleTestSelection = (testId: string) => {
    setSelectedTests(prev => 
      prev.includes(testId) 
        ? prev.filter(id => id !== testId)
        : [...prev, testId]
    );
  };

  const canProceedToGenerate = requirement && currentStep === 'generating';
  const canProceedToApprove = testSuite && currentStep === 'approving';
  const canProceedToRun = requirement && currentStep === 'synthesizing';

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Test Generation</h1>

             {/* Progress Steps */}
       <div className="mb-8">
         <div className="flex items-center justify-between">
           {['Input', 'Parse', 'View Parsed', 'Generate Tests', 'Approve', 'Generate Code', 'Run'].map((step, index) => (
             <div key={step} className="flex items-center">
               <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold ${
                 index === 0 ? 'bg-blue-600 text-white' :
                 index === 1 && currentStep === 'parsing' ? 'bg-blue-600 text-white' :
                 index === 2 && currentStep === 'parsed' ? 'bg-blue-600 text-white' :
                 index === 3 && currentStep === 'generating' ? 'bg-blue-600 text-white' :
                 index === 4 && currentStep === 'approving' ? 'bg-blue-600 text-white' :
                 index === 5 && currentStep === 'synthesizing' ? 'bg-blue-600 text-white' :
                 index === 6 && currentStep === 'running' ? 'bg-blue-600 text-white' :
                 'bg-gray-200 text-gray-600'
               }`}>
                 {index + 1}
               </div>
               <span className="ml-2 text-sm font-medium">{step}</span>
               {index < 6 && <div className="w-16 h-0.5 bg-gray-200 ml-2" />}
             </div>
           ))}
         </div>
          </div>

      {/* Error/Success Messages */}
      {error && (
        <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}
      {success && (
        <div className="mb-4 p-4 bg-green-100 border border-green-400 text-green-700 rounded">
          {success}
            </div>
          )}

      {/* Input Section */}
      <div className="bg-white p-6 rounded-lg shadow mb-6">
        <h2 className="text-xl font-semibold mb-4">Step 1: Input Requirement</h2>
        
        {/* Tabs */}
        <div className="flex border-b mb-4">
          <button
            className={`px-4 py-2 ${activeTab === 'text' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-500'}`}
            onClick={() => setActiveTab('text')}
          >
            Text Input
          </button>
          <button
            className={`px-4 py-2 ${activeTab === 'file' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-500'}`}
            onClick={() => setActiveTab('file')}
          >
            File Upload
          </button>
        </div>

        {activeTab === 'text' ? (
          <div>
            <textarea
              value={storyText}
              onChange={(e) => setStoryText(e.target.value)}
              placeholder="Enter your user story here..."
              className="w-full h-32 p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={currentStep !== 'input'}
            />
          </div>
        ) : (
          <div>
            <input
              type="file"
              accept=".txt,.md,.docx,.pdf"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="w-full p-3 border border-gray-300 rounded-md"
              disabled={currentStep !== 'input'}
            />
            <p className="text-sm text-gray-500 mt-2">Supported: .txt, .md, .docx, .pdf</p>
          </div>
        )}

                 <div className="mt-4 space-y-3">
           <div className="flex items-center">
             <label className="flex items-center">
               <input
                 type="checkbox"
                 checked={allowDuplicates}
                 onChange={(e) => setAllowDuplicates(e.target.checked)}
                 className="mr-2"
                 disabled={currentStep !== 'input'}
               />
               Allow duplicates
             </label>
           </div>
           <div className="flex items-center">
             <label className="flex items-center">
               <input
                 type="checkbox"
                 checked={autoGenerateCode}
                 onChange={(e) => setAutoGenerateCode(e.target.checked)}
                 className="mr-2"
                 disabled={currentStep !== 'input'}
               />
               Auto-generate code after test approval
             </label>
           </div>
         </div>

        <button
          onClick={handleParse}
          disabled={currentStep !== 'input' || (!storyText.trim() && !file)}
          className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {currentStep === 'parsing' ? 'Parsing...' : 'Parse Requirement'}
        </button>
      </div>

             {/* View Parsed Requirement Section */}
       {currentStep === 'parsed' && requirement && (
         <div className="bg-white p-6 rounded-lg shadow mb-6">
           <h2 className="text-xl font-semibold mb-4">Step 2: View Parsed Requirement</h2>
           <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
             <div>
               <h3 className="font-semibold text-gray-700">Requirement Details</h3>
               <div className="mt-2 space-y-2">
                 <p><strong>Title:</strong> {requirement.title}</p>
                 <p><strong>Actor:</strong> {requirement.actor}</p>
                 <p><strong>Goal:</strong> {requirement.goal}</p>
                 <p><strong>Acceptance Criteria:</strong> {requirement.ac_count}</p>
                 <p><strong>Session ID:</strong> <code className="text-xs bg-gray-100 p-1 rounded">{requirement.session_id}</code></p>
               </div>
             </div>
             <div>
               <h3 className="font-semibold text-gray-700">Original Input</h3>
               <div className="mt-2 p-3 bg-gray-50 rounded border">
                 <p className="text-sm text-gray-700">{storyText || (file ? `File: ${file.name}` : 'No input provided')}</p>
               </div>
             </div>
           </div>
           <button
             onClick={handleGenerate}
             className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
           >
             Generate Tests
           </button>
         </div>
       )}

       {/* Generate Tests Section */}
       {canProceedToGenerate && (
         <div className="bg-white p-6 rounded-lg shadow mb-6">
           <h2 className="text-xl font-semibold mb-4">Step 3: Generate Tests</h2>
           <p className="text-gray-600 mb-4">
             Requirement: <strong>{requirement.title}</strong> ({requirement.ac_count} acceptance criteria)
           </p>
           <button
             onClick={handleGenerate}
             disabled={currentStep !== 'generating'}
             className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
           >
             {currentStep === 'generating' ? 'Generating...' : 'Generate Tests'}
           </button>
         </div>
       )}

                    {/* Approve Tests Section */}
       {canProceedToApprove && testSuite && (
         <div className="bg-white p-6 rounded-lg shadow mb-6">
           <h2 className="text-xl font-semibold mb-4">Step 4: Review & Approve Tests</h2>
           <p className="text-gray-600 mb-4">
             Generated {testSuite.test_count} test cases
           </p>
           
           {/* BDD Test Preview - Table View */}
           <div className="mb-6">
             <div className="flex justify-between items-center mb-3">
               <h3 className="text-lg font-semibold">BDD Test Preview</h3>
               <div className="flex gap-2">
                 <button
                   onClick={() => {
                     const allIds = testSuite.test_cases.map(tc => tc.id);
                     setSelectedTests(allIds);
                   }}
                   className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                 >
                   Select All
                 </button>
                 <button
                   onClick={() => setSelectedTests([])}
                   className="px-3 py-1 text-sm bg-gray-600 text-white rounded hover:bg-gray-700"
                 >
                   Clear All
                 </button>
               </div>
             </div>
             
             <div className="overflow-x-auto">
               <table className="min-w-full border border-gray-200">
                 <thead className="bg-gray-50">
                   <tr>
                     <th className="p-3 border text-left w-16">
                       <input
                         type="checkbox"
                         checked={selectedTests.length === testSuite.test_cases.length}
                         onChange={(e) => {
                           if (e.target.checked) {
                             setSelectedTests(testSuite.test_cases.map(tc => tc.id));
                           } else {
                             setSelectedTests([]);
                           }
                         }}
                       />
                     </th>
                     <th className="p-3 border text-left font-semibold">TC ID</th>
                     <th className="p-3 border text-left font-semibold">Test Scenario</th>
                     <th className="p-3 border text-left font-semibold">BDD Test</th>
                     <th className="p-3 border text-left font-semibold">Priority</th>
                     <th className="p-3 border text-left font-semibold">Type</th>
                   </tr>
                 </thead>
                 <tbody>
                   {testSuite.test_cases.map((test) => (
                     <tr key={test.id} className="hover:bg-gray-50">
                       <td className="p-3 border">
                         <input
                           type="checkbox"
                           checked={selectedTests.includes(test.id)}
                           onChange={() => handleTestSelection(test.id)}
                         />
                       </td>
                       <td className="p-3 border font-mono text-sm">{test.id}</td>
                       <td className="p-3 border">{test.title}</td>
                       <td className="p-3 border">
                         <div className="font-mono text-xs bg-gray-100 p-2 rounded max-w-md">
                           <div className="text-green-600">Feature: {test.title.split(':')[0]}</div>
                           <div className="text-purple-600 mt-1">As a shopper</div>
                           <div className="text-purple-600">I want to test e-commerce functionality</div>
                           <div className="text-purple-600 mb-2">So that the website works correctly</div>
                           
                           <div className="text-gray-600 text-xs mb-1">Background:</div>
                           <div className="text-gray-700 mb-2">{test.preconditions?.[0] || 'Given I am on the e-commerce website'}</div>
                           
                           <div className="text-blue-600 font-semibold">Scenario: {test.title.split(':')[1] || test.title}</div>
                           <div className="text-gray-700 mt-1">
                             {test.steps?.map((step, idx) => (
                               <div key={idx} className="mb-1">
                                 {step.action === 'search.execute' && `When I search for "${step.params?.query || 'products'}"`}
                                 {step.action === 'cart.add_item' && 'When I click "Add to Cart"'}
                                 {step.action === 'navigation.goto' && `When I navigate to ${step.params?.target || 'the page'}`}
                                 {step.action === 'cart.apply_coupon' && `When I apply coupon "${step.params?.code || 'WELCOME10'}"`}
                                 {step.action === 'product.set_quantity' && `When I set quantity to ${step.params?.quantity || 1}`}
                                 {step.action === 'form.enter_zip' && `When I enter ZIP code "${step.params?.zip || '10001'}"`}
                                 {!['search.execute', 'cart.add_item', 'navigation.goto', 'cart.apply_coupon', 'product.set_quantity', 'form.enter_zip'].includes(step.action) && 
                                   `When I perform ${step.action.replace('.', ' ')}`}
                               </div>
                             )) || (
                               <>
                                 <div>When I perform the test action</div>
                                 <div>Then I should see the expected result</div>
                               </>
                             )}
                             
                             {test.data?.examples && (
                               <div className="mt-2 text-xs">
                                 <div className="text-gray-600">Examples:</div>
                                 <div className="bg-white p-1 rounded border">
                                   {test.data.examples.slice(0, 2).map((example: any, idx: number) => (
                                     <div key={idx} className="text-gray-700">
                                       {Object.entries(example).map(([key, value]) => `${key}: ${value}`).join(', ')}
                                     </div>
                                   ))}
                                 </div>
                               </div>
                             )}
                           </div>
                         </div>
                       </td>
                       <td className="p-3 border">
                         <span className="px-2 py-1 rounded text-xs bg-blue-100 text-blue-800">
                           {test.priority}
                         </span>
                       </td>
                       <td className="p-3 border">
                         <span className={`px-2 py-1 rounded text-xs ${
                           test.type === 'positive' ? 'bg-green-100 text-green-800' :
                           test.type === 'negative' ? 'bg-red-100 text-red-800' :
                           'bg-yellow-100 text-yellow-800'
                         }`}>
                           {test.type}
                         </span>
                       </td>
                     </tr>
                   ))}
                 </tbody>
               </table>
             </div>
           </div>

           <button
             onClick={handleApprove}
             disabled={selectedTests.length === 0}
             className="mt-4 px-6 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
           >
             Approve Selected Tests
           </button>
         </div>
       )}

             {/* Run Tests Section */}
       {canProceedToRun && (
         <div className="bg-white p-6 rounded-lg shadow mb-6">
           <h2 className="text-xl font-semibold mb-4">Step 6: Run Tests</h2>
          
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">UI Mode:</label>
              <select
                value={uiMode}
                onChange={(e) => setUiMode(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-md"
              >
                <option value="real">Real</option>
                <option value="mock">Mock</option>
            </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">API Mode:</label>
              <select
                value={apiMode}
                onChange={(e) => setApiMode(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-md"
              >
                <option value="real">Real</option>
                <option value="mock">Mock</option>
                <option value="stub">Stub</option>
            </select>
            </div>
          </div>

          <div className="mb-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={autoPR}
                onChange={(e) => setAutoPR(e.target.checked)}
                className="mr-2"
              />
              Auto-PR on pass
            </label>
          </div>

          <button
            onClick={handleRun}
            disabled={currentStep !== 'synthesizing'}
            className="px-6 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            Run Tests
          </button>
        </div>
      )}

             {/* Generated Code Location */}
       {currentStep === 'synthesizing' && (
         <div className="bg-white p-6 rounded-lg shadow mb-6">
           <h2 className="text-xl font-semibold mb-4">Step 5: Code Generated Successfully!</h2>
           <div className="bg-green-50 border border-green-200 rounded-lg p-4">
             <h3 className="font-semibold text-green-800 mb-2">✅ Code Generation Complete</h3>
             <p className="text-green-700 mb-3">
               Your test code has been automatically generated during approval and saved to:
             </p>
             <div className="bg-white p-3 rounded border">
               <p className="font-mono text-sm">
                 <strong>Directory:</strong> tests/{requirement?.session_id}/
               </p>
               <p className="font-mono text-sm">
                 <strong>Structure:</strong>
               </p>
               <ul className="font-mono text-xs ml-4 mt-1">
                 <li>📁 <strong>features/</strong> - BDD feature files</li>
                 <li>&nbsp;&nbsp;&nbsp;• search.feature - Search functionality</li>
                 <li>&nbsp;&nbsp;&nbsp;• cart.feature - Cart operations</li>
                 <li>&nbsp;&nbsp;&nbsp;• checkout.feature - Checkout process</li>
                 <li>📁 <strong>steps/</strong> - Step definitions by area</li>
                 <li>&nbsp;&nbsp;&nbsp;📁 search/ - Search step definitions</li>
                 <li>&nbsp;&nbsp;&nbsp;📁 cart/ - Cart step definitions</li>
                 <li>&nbsp;&nbsp;&nbsp;📁 checkout/ - Checkout step definitions</li>
                 <li>📄 conftest.py - Shared test fixtures</li>
                 <li>📄 locators.yml - Shared UI element locators</li>
               </ul>
             </div>
             <p className="text-green-700 mt-3 text-sm">
               <strong>Note:</strong> Code is generated automatically when you approve tests. 
               You can now run the tests from Step 6 below.
             </p>
           </div>
         </div>
       )}

       {/* Run Status */}
       {runStatus && (
         <div className="bg-white p-6 rounded-lg shadow">
           <h2 className="text-xl font-semibold mb-4">Run Status</h2>
           <div className="bg-gray-50 p-4 rounded mb-4">
             <p><strong>Run ID:</strong> {runStatus.id}</p>
             <p><strong>Status:</strong> {runStatus.status}</p>
             <p><strong>Created:</strong> {new Date(runStatus.created_at).toLocaleString()}</p>
           </div>
           
           {/* Test Logs */}
           {(runStatus as any).logs && (runStatus as any).logs.length > 0 && (
             <div className="mb-4">
               <h3 className="text-lg font-semibold mb-2">📋 Execution Logs</h3>
               {(runStatus as any).logs.map((log: any, idx: number) => (
                 <div key={idx} className="mb-3 border rounded">
                   <div className="bg-gray-200 px-3 py-1 text-sm font-mono flex justify-between">
                     <span>📄 {log.file}</span>
                     <span className="text-gray-600">{(log.size / 1024).toFixed(1)} KB</span>
                   </div>
                   <pre className="text-xs bg-white p-3 overflow-x-auto max-h-40 border-t">
                     {log.content}
                   </pre>
                 </div>
               ))}
             </div>
           )}
           
           {/* Test Reports */}
           {(runStatus as any).reports && (runStatus as any).reports.length > 0 && (
             <div className="mb-4">
               <h3 className="text-lg font-semibold mb-2">📊 Test Reports</h3>
               <div className="space-y-2">
                 {(runStatus as any).reports.map((report: any, idx: number) => (
                   <div key={idx} className="flex items-center justify-between p-3 bg-blue-50 rounded border">
                     <div>
                       <span className="font-medium">{report.name}</span>
                       <span className="ml-2 px-2 py-1 bg-blue-200 text-blue-800 text-xs rounded">
                         {report.type.toUpperCase()}
                       </span>
                       {report.size && (
                         <span className="ml-2 text-sm text-gray-600">
                           ({(report.size / 1024).toFixed(1)} KB)
                         </span>
                       )}
                     </div>
                     <a
                       href={`http://localhost:8080${report.url}`}
                       target="_blank"
                       rel="noopener noreferrer"
                       className="bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-700 transition-colors"
                     >
                       📄 View Report
                     </a>
                   </div>
                 ))}
               </div>
             </div>
           )}
           
           </div>
          )}
        </div>
  );
};

// Runs Component
const Runs: React.FC = () => {
  const [runs, setRuns] = useState<RunStatus[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRuns = async () => {
      try {
        // For now, we'll show a placeholder since we need to implement the runs endpoint
        setRuns([]);
      } catch (error) {
        console.error('Failed to fetch runs:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchRuns();
  }, []);

  if (loading) return <div className="p-6">Loading runs...</div>;

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Test Runs</h1>
      <div className="bg-white p-6 rounded-lg shadow">
        <p className="text-gray-600">Run history will be displayed here. This feature is coming soon.</p>
      </div>
    </div>
  );
};

// Main App Component
const App: React.FC = () => {
  const location = useLocation();

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <h1 className="text-2xl font-bold text-gray-900">SpecWeaver</h1>
            <nav className="flex space-x-8">
              <Link
                to="/"
                className={`text-sm font-medium ${
                  location.pathname === '/' ? 'text-blue-600' : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                Dashboard
              </Link>
              <Link
                to="/generate"
                className={`text-sm font-medium ${
                  location.pathname === '/generate' ? 'text-blue-600' : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                Test Generation
              </Link>
              <Link
                to="/runs"
                className={`text-sm font-medium ${
                  location.pathname === '/runs' ? 'text-blue-600' : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                Runs
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/generate" element={<TestGeneration />} />
          <Route path="/runs" element={<Runs />} />
        </Routes>
      </main>
    </div>
  );
};

export default App;
