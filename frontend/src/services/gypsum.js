/**
 * Gypsum Integration Service for VoiceForge
 * Provides persona-aware content generation using Gypsum positioning data
 */

export class GypsumVoiceForgeClient {
  constructor(apiUrl = 'http://localhost:3001', apiKey = null) { // Gypsum API server port
    this.apiUrl = apiUrl;
    this.apiKey = apiKey;
    this.cache = new Map(); // Simple in-memory cache
  }

  /**
   * Get request headers with authentication
   */
  getHeaders() {
    const headers = {
      'Content-Type': 'application/json'
    };
    
    if (this.apiKey) {
      headers['Authorization'] = `Bearer ${this.apiKey}`;
    }
    
    return headers;
  }

  /**
   * Fetch all context data for a user
   */
  async fetchAllContext(userId) {
    const cacheKey = `context_${userId}`;
    
    // Check cache first (5-minute TTL)
    if (this.cache.has(cacheKey)) {
      const cached = this.cache.get(cacheKey);
      if (Date.now() - cached.timestamp < 5 * 60 * 1000) {
        console.log('🗂️ Using cached context data');
        return cached.data;
      }
    }

    try {
      console.log('🌐 Fetching fresh context data from Gypsum APIs...');
      
      const [messagingRes, personasRes, positioningRes] = await Promise.all([
        fetch(`${this.apiUrl}/api/messaging/context?user_id=${userId}`, {
          headers: this.getHeaders()
        }),
        fetch(`${this.apiUrl}/api/personas/context?user_id=${userId}`, {
          headers: this.getHeaders()
        }),
        fetch(`${this.apiUrl}/api/positioning/context?user_id=${userId}`, {
          headers: this.getHeaders()
        })
      ]);

      console.log('📊 API Response Status:');
      console.log('- Messaging:', messagingRes.status, messagingRes.ok);
      console.log('- Personas:', personasRes.status, personasRes.ok);
      console.log('- Positioning:', positioningRes.status, positioningRes.ok);

      if (!messagingRes.ok || !personasRes.ok || !positioningRes.ok) {
        console.error('❌ One or more API calls failed:');
        if (!messagingRes.ok) console.error('Messaging API failed:', await messagingRes.text());
        if (!personasRes.ok) console.error('Personas API failed:', await personasRes.text());
        if (!positioningRes.ok) console.error('Positioning API failed:', await positioningRes.text());
        throw new Error('Failed to fetch context data');
      }

      const messaging = await messagingRes.json();
      const personas = await personasRes.json();
      const positioning = await positioningRes.json();
      
      console.log('📦 Raw API Responses:');
      console.log('- Messaging:', messaging);
      console.log('- Personas:', personas);
      console.log('- Positioning:', positioning);
      
      const context = {
        messaging,
        personas,
        positioning
      };

      // Cache the result
      this.cache.set(cacheKey, {
        data: context,
        timestamp: Date.now()
      });

      return context;
    } catch (error) {
      console.error('❌ Error fetching Gypsum context:', error);
      throw error;
    }
  }

  /**
   * Generate enhanced AI prompt with Gypsum context
   */
  generateEnhancedPrompt(context, selectedPersonaId, contentType, additionalInstructions = '') {
    const { messaging, personas, positioning } = context;
    const selectedPersona = personas.personas.find(p => p.id === selectedPersonaId);

    if (!selectedPersona) {
      throw new Error('Selected persona not found');
    }

    return `You are creating ${contentType} for a specific target audience. Use the following context to create highly personalized, on-brand content:

## TARGET PERSONA
Role: ${selectedPersona.role}
Seniority Level: ${selectedPersona.seniority_level}
Industry: ${selectedPersona.industry}
Company Size: ${selectedPersona.company_size}
Communication Style: ${selectedPersona.communication_style || 'Professional'}

## PERSONA PAIN POINTS
${selectedPersona.pain_points?.map(point => `- ${point}`).join('\n') || 'No specific pain points available'}

## PERSONA GOALS
${selectedPersona.goals?.map(goal => `- ${goal}`).join('\n') || 'No specific goals available'}

## TECH STACK & CONTEXT
${selectedPersona.tech_stack?.join(', ') || 'No tech stack specified'}

## COMPANY MESSAGING
Elevator Pitch: ${messaging.elevator_pitch}
Headline: ${messaging.headline_message}
Tone: ${messaging.tone_voice}
Key Differentiators: ${messaging.key_differentiators?.join(', ') || 'No differentiators specified'}

## POSITIONING
Target Market: ${positioning.target_market}
Category: ${positioning.category}
Value Proposition: ${positioning.value_proposition}
Differentiation: ${positioning.differentiation}
Proof Points: ${positioning.proof_points?.join(', ') || 'No proof points available'}

## CONTENT REQUIREMENTS
${additionalInstructions}

Generate ${contentType} that:
1. Addresses the specific pain points of ${selectedPersona.role}
2. Speaks in the appropriate tone for ${selectedPersona.seniority_level} level
3. Uses language and examples relevant to ${selectedPersona.industry}
4. Incorporates our key differentiators and proof points
5. Maintains consistency with our brand messaging
6. Is optimized for ${selectedPersona.communication_style || 'professional'} communication style

Make the content feel personally relevant to someone in their role, industry, and company size.`;
  }

  /**
   * Validate API connection and user access
   */
  async validateConnection(userId) {
    try {
      console.log('🔍 Validating Gypsum connection for user:', userId);
      
      const response = await fetch(`${this.apiUrl}/health`, {
        headers: this.getHeaders()
      });

      console.log('🌡️ Health check response:', response.status, response.ok);

      if (!response.ok) {
        throw new Error('API server not responding');
      }

      // Test user access with multiple possible endpoints
      const possibleEndpoints = [
        `/api/messaging/context?user_id=${userId}`,
        `/api/v1/messaging/context?user_id=${userId}`,
        `/messaging/context?user_id=${userId}`,
        `/api/messaging?user_id=${userId}`
      ];
      
      for (const endpoint of possibleEndpoints) {
        try {
          console.log(`🗺️ Testing endpoint: ${this.apiUrl}${endpoint}`);
          
          const testResponse = await fetch(
            `${this.apiUrl}${endpoint}`,
            { headers: this.getHeaders() }
          );
          
          console.log(`📈 Response for ${endpoint}:`, testResponse.status, testResponse.ok);
          
          if (testResponse.ok) {
            console.log(`✅ Found working endpoint: ${endpoint}`);
            return {
              connected: true,
              userAccess: true,
              status: testResponse.status,
              workingEndpoint: endpoint
            };
          } else {
            const errorText = await testResponse.text();
            console.log(`❌ ${endpoint} failed:`, testResponse.status, errorText.substring(0, 100));
          }
        } catch (e) {
          console.log(`❌ Failed endpoint: ${endpoint}`, e.message);
        }
      }

      return {
        connected: true,
        userAccess: false,
        error: 'No working API endpoints found'
      };
    } catch (error) {
      console.error('❌ Validation failed:', error);
      return {
        connected: false,
        userAccess: false,
        error: error.message
      };
    }
  }
}

// Singleton instance for easy import
export const gypsumClient = new GypsumVoiceForgeClient();

// Remove hardcoded demo user - now passed dynamically
