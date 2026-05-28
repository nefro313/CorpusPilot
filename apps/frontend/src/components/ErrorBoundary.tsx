import { Component, type ErrorInfo, type ReactNode } from "react";

interface Props {
  fallback?: (error: Error, reset: () => void) => ReactNode;
  children: ReactNode;
}

interface State {
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    // Surfaced to Grafana/Sentry once the user wires either provider; until
    // then the console is the only sink.
    console.error("UI error boundary caught:", error, info);
  }

  reset = () => this.setState({ error: null });

  render() {
    const { error } = this.state;
    if (!error) return this.props.children;
    if (this.props.fallback) return this.props.fallback(error, this.reset);
    return (
      <div className="error-boundary">
        <h2>Something broke in the UI.</h2>
        <p>{error.message}</p>
        <button type="button" onClick={this.reset}>
          Reset view
        </button>
      </div>
    );
  }
}
