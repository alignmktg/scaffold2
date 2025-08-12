import type {
	ChatRequest,
	ChatResponse,
	StreamChatResponse,
	AuthResponse,
	HealthCheck,
	User,
	TaskRequest,
	TaskResponse,
	Document,
	DocumentSearchRequest,
	OllamaModelInfo,
} from "../types";

export class ApiClient {
	private baseUrl: string;
	private token?: string;

	constructor(baseUrl: string = "/api") {
		this.baseUrl = baseUrl;
	}

	setToken(token: string) {
		this.token = token;
	}

	private async request<T>(
		endpoint: string,
		options: RequestInit = {}
	): Promise<T> {
		const url = `${this.baseUrl}${endpoint}`;
		const headers: HeadersInit = {
			"Content-Type": "application/json",
			...options.headers,
		};

		if (this.token) {
			headers.Authorization = `Bearer ${this.token}`;
		}

		const response = await fetch(url, {
			...options,
			headers,
		});

		if (!response.ok) {
			const error = await response
				.json()
				.catch(() => ({ detail: "Unknown error" }));
			throw new Error(error.detail || `HTTP ${response.status}`);
		}

		return response.json();
	}

	// Health check
	async healthCheck(): Promise<HealthCheck> {
		return this.request<HealthCheck>("/health");
	}

	// Authentication
	async verifyToken(token: string): Promise<AuthResponse> {
		return this.request<AuthResponse>("/auth/verify", {
			method: "POST",
			body: JSON.stringify({ token }),
		});
	}

	async getCurrentUser(): Promise<User> {
		return this.request<User>("/auth/me");
	}

	// Chat
	async chatCompletion(request: ChatRequest): Promise<ChatResponse> {
		return this.request<ChatResponse>("/ai/chat", {
			method: "POST",
			body: JSON.stringify(request),
		});
	}

	async *chatCompletionStream(
		request: ChatRequest
	): AsyncGenerator<StreamChatResponse> {
		const url = `${this.baseUrl}/ai/chat/stream`;
		const headers: HeadersInit = {
			"Content-Type": "application/json",
		};

		if (this.token) {
			headers.Authorization = `Bearer ${this.token}`;
		}

		const response = await fetch(url, {
			method: "POST",
			headers,
			body: JSON.stringify(request),
		});

		if (!response.ok) {
			const error = await response
				.json()
				.catch(() => ({ detail: "Unknown error" }));
			throw new Error(error.detail || `HTTP ${response.status}`);
		}

		const reader = response.body?.getReader();
		if (!reader) {
			throw new Error("No response body");
		}

		const decoder = new TextDecoder();
		let buffer = "";

		try {
			while (true) {
				const { done, value } = await reader.read();
				if (done) break;

				buffer += decoder.decode(value, { stream: true });
				const lines = buffer.split("\n");
				buffer = lines.pop() || "";

				for (const line of lines) {
					if (line.startsWith("data: ")) {
						const data = line.slice(6);
						if (data === "[DONE]") return;

						try {
							const parsed = JSON.parse(data);
							yield parsed as StreamChatResponse;
						} catch (e) {
							// Skip invalid JSON
						}
					}
				}
			}
		} finally {
			reader.releaseLock();
		}
	}

	async listModels(): Promise<{
		models: Array<{ id: string; provider: string; name: string }>;
	}> {
		return this.request("/ai/models");
	}

	// Workers (if enabled)
	async submitTask(request: TaskRequest): Promise<TaskResponse> {
		return this.request<TaskResponse>("/workers/tasks", {
			method: "POST",
			body: JSON.stringify(request),
		});
	}

	async getTaskStatus(taskId: string): Promise<any> {
		return this.request(`/workers/tasks/${taskId}`);
	}

	// RAG (if enabled)
	async searchDocuments(request: DocumentSearchRequest): Promise<Document[]> {
		return this.request<Document[]>("/rag/search", {
			method: "POST",
			body: JSON.stringify(request),
		});
	}

	async ingestDocuments(
		documents: string[],
		metadatas?: any[]
	): Promise<any> {
		return this.request("/rag/ingest", {
			method: "POST",
			body: JSON.stringify({
				documents,
				metadatas: metadatas || [],
			}),
		});
	}

	async listCollections(): Promise<{ collections: string[]; count: number }> {
		return this.request("/rag/collections");
	}

	// Ollama (if enabled)
	async ollamaChat(request: ChatRequest): Promise<ChatResponse> {
		return this.request<ChatResponse>("/ollama/chat", {
			method: "POST",
			body: JSON.stringify(request),
		});
	}

	async *ollamaChatStream(
		request: ChatRequest
	): AsyncGenerator<StreamChatResponse> {
		const url = `${this.baseUrl}/ollama/chat/stream`;
		const headers: HeadersInit = {
			"Content-Type": "application/json",
		};

		if (this.token) {
			headers.Authorization = `Bearer ${this.token}`;
		}

		const response = await fetch(url, {
			method: "POST",
			headers,
			body: JSON.stringify(request),
		});

		if (!response.ok) {
			const error = await response
				.json()
				.catch(() => ({ detail: "Unknown error" }));
			throw new Error(error.detail || `HTTP ${response.status}`);
		}

		const reader = response.body?.getReader();
		if (!reader) {
			throw new Error("No response body");
		}

		const decoder = new TextDecoder();
		let buffer = "";

		try {
			while (true) {
				const { done, value } = await reader.read();
				if (done) break;

				buffer += decoder.decode(value, { stream: true });
				const lines = buffer.split("\n");
				buffer = lines.pop() || "";

				for (const line of lines) {
					if (line.startsWith("data: ")) {
						const data = line.slice(6);
						if (data === "[DONE]") return;

						try {
							const parsed = JSON.parse(data);
							yield parsed as StreamChatResponse;
						} catch (e) {
							// Skip invalid JSON
						}
					}
				}
			}
		} finally {
			reader.releaseLock();
		}
	}

	async listOllamaModels(): Promise<OllamaModelInfo[]> {
		return this.request<OllamaModelInfo[]>("/ollama/models");
	}

	async pullOllamaModel(modelName: string): Promise<any> {
		return this.request("/ollama/models/pull", {
			method: "POST",
			body: JSON.stringify({ model_name: modelName }),
		});
	}

	async deleteOllamaModel(modelName: string): Promise<any> {
		return this.request(`/ollama/models/${modelName}`, {
			method: "DELETE",
		});
	}

	async generateEmbeddings(
		text: string,
		model: string = "llama2"
	): Promise<any> {
		return this.request("/ollama/embeddings", {
			method: "POST",
			body: JSON.stringify({ text, model }),
		});
	}
}

// Create default client instance
export const apiClient = new ApiClient();
