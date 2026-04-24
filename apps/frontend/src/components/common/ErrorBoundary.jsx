import { Component } from 'react';

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    console.error('ErrorBoundary caught:', error, info.componentStack);
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-[60vh] items-center justify-center bg-surface px-4">
          <div className="max-w-md text-center">
            <div className="mb-4 text-5xl">⚠️</div>
            <h2 className="mb-2 text-xl font-light  tracking-tight text-on-surface">
              Something went wrong
            </h2>
            <p className="mb-6 text-sm font-light text-outline-muted">
              An unexpected error occurred. Please try again.
            </p>
            <button
              type="button"
              onClick={this.handleRetry}
              className="border border-black bg-black px-6 py-2.5    text-white transition-colors duration-100 hover:bg-white hover:text-black"
            >
              Try again
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
