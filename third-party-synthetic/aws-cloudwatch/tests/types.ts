
type Handler = (...params: any[]) => any;
type HandlerList = { [index: string]: Handler[] };

interface PageResponse {
    status: () => number,
}

interface Page {
    title: () => Promise<string>;
    url: () => string;
    waitFor: () => void;
    on: (name: string, handler: Handler) => void;
    goto: (url: string, options: any) => PageResponse;
    evaluate: <T>(expression: () => T) => T;
}

interface MockPage extends Page {
    _pageHandlers: HandlerList;
}

interface HttpResponse {
    statusCode: number;
    on: (name: string, handler: Handler) => void;
    setEncoding: () => void;
}

interface MockHttpResponse extends HttpResponse {
    _responseHandlers: HandlerList;
}

interface HttpRequest {
    on: (name: string, handler: Handler) => void;
    end: () => void;
    write: (chunk: string) => void;
}

interface MockHttpRequest extends HttpRequest {
    _originalEnd: () => void;
    _requestHandlers: HandlerList;
    _body?: any;
}

interface HttpModule {
    request: () => MockHttpRequest;
    get: () => MockHttpRequest;
}

interface MockHttpModule extends HttpModule {
    _mockRequests: {
        request: MockHttpRequest;
        response: MockHttpResponse;
    }[];
}
