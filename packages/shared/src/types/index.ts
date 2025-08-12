import { z } from "zod";

// Chat message schema
export const ChatMessageSchema = z.object({
	role: z.enum(["user", "assistant", "system"]),
	content: z.string(),
});

export type ChatMessage = z.infer<typeof ChatMessageSchema>;

// Chat request schema
export const ChatRequestSchema = z.object({
	messages: z.array(ChatMessageSchema),
	model: z.string().default("gpt-3.5-turbo"),
	provider: z.string().default("openai"),
	temperature: z.number().min(0).max(2).default(0.7),
	max_tokens: z.number().min(1).max(4000).default(1000),
	stream: z.boolean().default(false),
});

export type ChatRequest = z.infer<typeof ChatRequestSchema>;

// Chat response schema
export const ChatResponseSchema = z.object({
	id: z.string(),
	object: z.literal("chat.completion"),
	created: z.number(),
	model: z.string(),
	choices: z.array(
		z.object({
			index: z.number(),
			message: z.object({
				role: z.literal("assistant"),
				content: z.string(),
			}),
			finish_reason: z.string().optional(),
		})
	),
	usage: z.object({
		prompt_tokens: z.number(),
		completion_tokens: z.number(),
		total_tokens: z.number(),
	}),
});

export type ChatResponse = z.infer<typeof ChatResponseSchema>;

// Streaming chat response schema
export const StreamChatResponseSchema = z.object({
	id: z.string(),
	object: z.literal("chat.completion.chunk"),
	created: z.number(),
	model: z.string(),
	choices: z.array(
		z.object({
			index: z.number(),
			delta: z.object({
				role: z.literal("assistant").optional(),
				content: z.string().optional(),
			}),
			finish_reason: z.string().optional(),
		})
	),
});

export type StreamChatResponse = z.infer<typeof StreamChatResponseSchema>;

// User schema
export const UserSchema = z.object({
	user_id: z.string(),
	email: z.string().email().optional(),
	role: z.string().default("user"),
});

export type User = z.infer<typeof UserSchema>;

// Auth response schema
export const AuthResponseSchema = z.object({
	valid: z.boolean(),
	user: UserSchema.optional(),
	error: z.string().optional(),
});

export type AuthResponse = z.infer<typeof AuthResponseSchema>;

// Health check schema
export const HealthCheckSchema = z.object({
	status: z.string(),
	timestamp: z.string(),
	version: z.string().optional(),
	environment: z.string().optional(),
});

export type HealthCheck = z.infer<typeof HealthCheckSchema>;

// API Error schema
export const ApiErrorSchema = z.object({
	detail: z.string(),
	status_code: z.number().optional(),
});

export type ApiError = z.infer<typeof ApiErrorSchema>;

// Model info schema
export const ModelInfoSchema = z.object({
	id: z.string(),
	provider: z.string(),
	name: z.string(),
});

export type ModelInfo = z.infer<typeof ModelInfoSchema>;

// Task request schema
export const TaskRequestSchema = z.object({
	data: z.record(z.any()),
});

export type TaskRequest = z.infer<typeof TaskRequestSchema>;

// Task response schema
export const TaskResponseSchema = z.object({
	task_id: z.string(),
	status: z.string(),
	message: z.string(),
});

export type TaskResponse = z.infer<typeof TaskResponseSchema>;

// Document schema
export const DocumentSchema = z.object({
	id: z.string(),
	document: z.string(),
	metadata: z.record(z.any()),
	distance: z.number().optional(),
});

export type Document = z.infer<typeof DocumentSchema>;

// Document search request schema
export const DocumentSearchRequestSchema = z.object({
	query: z.string(),
	n_results: z.number().min(1).max(20).default(5),
	filter_metadata: z.record(z.any()).default({}),
});

export type DocumentSearchRequest = z.infer<typeof DocumentSearchRequestSchema>;

// Ollama model info schema
export const OllamaModelInfoSchema = z.object({
	name: z.string(),
	size: z.number(),
	modified_at: z.string().optional(),
	digest: z.string().optional(),
});

export type OllamaModelInfo = z.infer<typeof OllamaModelInfoSchema>;
