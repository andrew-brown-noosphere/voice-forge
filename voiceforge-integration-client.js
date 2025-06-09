/**
 * Sample VoiceForge Integration Client
 * This demonstrates how VoiceForge would integrate with Gypsum APIs
 */

class GypsumVoiceForgeClient {
  constructor(apiUrl, apiKey = null) {
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
        return cached.data;
      }
    }

    try {
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

      if (!messagingRes.ok || !personasRes.ok || !positioningRes.ok) {
        throw new Error('Failed to fetch context data');
      }

      const context = {
        messaging: await messagingRes.json(),
        personas: await personasRes.json(),
        positioning: await positioningRes.json()
      };

      // Cache the result
      this.cache.set(cacheKey, {
        data: context,
        timestamp: Date.now()
      });

      return context;
    } catch (error) {
      console.error('Error fetching Gypsum context:', error);
      throw error;
    }
  }

  /**
   * Fetch specific persona context
   */
  async fetchPersonaContext(userId, personaId) {
    try {
      const response = await fetch(
        `${this.apiUrl}/api/personas/${personaId}/context?user_id=${userId}`,
        { headers: this.getHeaders() }
      );

      if (!response.ok) {
        throw new Error(`Failed to fetch persona context: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching persona context:', error);
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

    return `
You are creating ${contentType} for a specific target audience. Use the following context to create highly personalized, on-brand content:

## TARGET PERSONA
Role: ${selectedPersona.role}
Seniority Level: ${selectedPersona.seniority_level}
Industry: ${selectedPersona.industry}
Company Size: ${selectedPersona.company_size}
Communication Style: ${selectedPersona.communication_style}

## PERSONA PAIN POINTS
${selectedPersona.pain_points.map(point => `- ${point}`).join('\n')}

## PERSONA GOALS
${selectedPersona.goals.map(goal => `- ${goal}`).join('\n')}

## TECH STACK & CONTEXT
${selectedPersona.tech_stack.join(', ')}

## COMPANY MESSAGING
Elevator Pitch: ${messaging.elevator_pitch}
Headline: ${messaging.headline_message}
Tone: ${messaging.tone_voice}
Key Differentiators: ${messaging.key_differentiators.join(', ')}

## POSITIONING
Target Market: ${positioning.target_market}
Category: ${positioning.category}
Value Proposition: ${positioning.value_proposition}
Differentiation: ${positioning.differentiation}
Proof Points: ${positioning.proof_points.join(', ')}

## CONTENT REQUIREMENTS
${additionalInstructions}

Generate ${contentType} that:
1. Addresses the specific pain points of ${selectedPersona.role}
2. Speaks in the appropriate tone for ${selectedPersona.seniority_level} level
3. Uses language and examples relevant to ${selectedPersona.industry}
4. Incorporates our key differentiators and proof points
5. Maintains consistency with our brand messaging
6. Is optimized for ${selectedPersona.communication_style} communication style

Make the content feel personally relevant to someone in their role, industry, and company size.
    `.trim();
  }

  /**
   * Get content suggestions based on persona and funnel stage
   */
  getContentSuggestions(persona, funnelStage = 'awareness') {
    const suggestions = {
      awareness: {
        'executive': [
          'Industry trend analysis blog post',
          'Strategic whitepaper',
          'Executive briefing document',
          'Industry report summary'
        ],
        'director': [
          'Solution comparison guide',
          'ROI calculator content',
          'Best practices article',
          'Implementation case study'
        ],
        'manager': [
          'How-to guide',
          'Technical tutorial',
          'Feature comparison chart',
          'Problem-solving blog post'
        ],
        'individual': [
          'Technical deep-dive article',
          'Code examples and tutorials',
          'Tool comparison review',
          'Hands-on demo content'
        ]
      },
      consideration: {
        'executive': [
          'Business case template',
          'Vendor comparison matrix',
          'Implementation timeline',
          'Risk assessment guide'
        ],
        'director': [
          'Detailed product demo',
          'Implementation roadmap',
          'Team training plan',
          'Success metrics framework'
        ],
        'manager': [
          'Feature deep-dive',
          'Integration guide',
          'Team adoption strategy',
          'Performance benchmarks'
        ],
        'individual': [
          'Technical specifications',
          'API documentation',
          'Hands-on trial guide',
          'Developer resources'
        ]
      },
      decision: {
        'executive': [
          'Executive summary proposal',
          'Stakeholder presentation',
          'Contract negotiation guide',
          'Implementation proposal'
        ],
        'director': [
          'Detailed implementation plan',
          'Team onboarding strategy',
          'Success measurement plan',
          'Support and training outline'
        ],
        'manager': [
          'Team rollout plan',
          'Training curriculum',
          'Success criteria checklist',
          'Quick wins identification'
        ],
        'individual': [
          'Getting started guide',
          'Quick setup tutorial',
          'Advanced features overview',
          'Troubleshooting guide'
        ]
      }
    };

    return suggestions[funnelStage]?.[persona.seniority_level] || [];
  }

  /**
   * Generate content variations for A/B testing
   */
  generateContentVariations(basePrompt, variationTypes = ['tone', 'length', 'focus']) {
    const variations = [];

    if (variationTypes.includes('tone')) {
      variations.push({
        type: 'tone_formal',
        prompt: basePrompt + '\n\nGenerate this content with a formal, professional tone suitable for enterprise decision-makers.'
      });
      
      variations.push({
        type: 'tone_casual',
        prompt: basePrompt + '\n\nGenerate this content with a conversational, approachable tone that feels like advice from a trusted colleague.'
      });
    }

    if (variationTypes.includes('length')) {
      variations.push({
        type: 'length_concise',
        prompt: basePrompt + '\n\nKeep this content concise and scannable - focus on key points that busy professionals can quickly digest.'
      });
      
      variations.push({
        type: 'length_detailed',
        prompt: basePrompt + '\n\nProvide comprehensive, detailed content that thoroughly addresses all aspects of the topic.'
      });
    }

    if (variationTypes.includes('focus')) {
      variations.push({
        type: 'focus_problem',
        prompt: basePrompt + '\n\nFocus primarily on the problems and pain points, establishing strong problem-solution fit.'
      });
      
      variations.push({
        type: 'focus_solution',
        prompt: basePrompt + '\n\nFocus primarily on our solution capabilities and unique benefits.'
      });
    }

    return variations;
  }

  /**
   * Validate API connection and user access
   */
  async validateConnection(userId) {
    try {
      const response = await fetch(`${this.apiUrl}/health`, {
        headers: this.getHeaders()
      });

      if (!response.ok) {
        throw new Error('API server not responding');
      }

      // Test user access
      const testResponse = await fetch(
        `${this.apiUrl}/api/messaging/context?user_id=${userId}`,
        { headers: this.getHeaders() }
      );

      return {
        connected: true,
        userAccess: testResponse.ok,
        status: testResponse.status
      };
    } catch (error) {
      return {
        connected: false,
        userAccess: false,
        error: error.message
      };
    }
  }
}

// Example usage for VoiceForge integration
class VoiceForgeContentGenerator {
  constructor() {
    this.gypsumClient = new GypsumVoiceForgeClient(
      process.env.GYPSUM_API_URL || 'http://localhost:3001',
      process.env.GYPSUM_API_KEY
    );
  }

  /**
   * Initialize content generation with Gypsum context
   */
  async initializeWithContext(userId) {
    try {
      // Validate connection first
      const validation = await this.gypsumClient.validateConnection(userId);
      if (!validation.connected) {
        throw new Error('Cannot connect to Gypsum API');
      }

      // Fetch all context data
      this.context = await this.gypsumClient.fetchAllContext(userId);
      this.userId = userId;
      
      console.log('VoiceForge initialized with Gypsum context:');
      console.log(`- ${this.context.personas.personas.length} personas available`);
      console.log(`- Messaging framework loaded`);
      console.log(`- Positioning framework loaded`);
      
      return this.context;
    } catch (error) {
      console.error('Failed to initialize VoiceForge with Gypsum context:', error);
      throw error;
    }
  }

  /**
   * Generate content for specific persona and content type
   */
  async generatePersonalizedContent(personaId, contentType, additionalInstructions = '') {
    if (!this.context) {
      throw new Error('VoiceForge not initialized with Gypsum context');
    }

    try {
      // Generate enhanced prompt
      const prompt = this.gypsumClient.generateEnhancedPrompt(
        this.context,
        personaId,
        contentType,
        additionalInstructions
      );

      // Here you would call your AI service (OpenAI, Anthropic, etc.)
      // For demo purposes, we'll return the prompt
      return {
        prompt,
        persona: this.context.personas.personas.find(p => p.id === personaId),
        contentType,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error('Error generating personalized content:', error);
      throw error;
    }
  }

  /**
   * Get available personas for selection
   */
  getAvailablePersonas() {
    if (!this.context) {
      throw new Error('VoiceForge not initialized with Gypsum context');
    }

    return this.context.personas.personas.map(persona => ({
      id: persona.id,
      role: persona.role,
      seniority_level: persona.seniority_level,
      industry: persona.industry,
      company_size: persona.company_size
    }));
  }

  /**
   * Get content suggestions for a persona
   */
  getContentSuggestions(personaId, funnelStage = 'awareness') {
    if (!this.context) {
      throw new Error('VoiceForge not initialized with Gypsum context');
    }

    const persona = this.context.personas.personas.find(p => p.id === personaId);
    if (!persona) {
      throw new Error('Persona not found');
    }

    return this.gypsumClient.getContentSuggestions(persona, funnelStage);
  }
}

// Demo usage example
async function demoVoiceForgeIntegration() {
  const contentGenerator = new VoiceForgeContentGenerator();
  const demoUserId = '123e4567-e89b-12d3-a456-426614174000';

  try {
    // Initialize with Gypsum context
    console.log('Initializing VoiceForge with Gypsum context...');
    await contentGenerator.initializeWithContext(demoUserId);

    // Get available personas
    const personas = contentGenerator.getAvailablePersonas();
    console.log('\nAvailable personas:');
    personas.forEach((persona, index) => {
      console.log(`${index + 1}. ${persona.role} (${persona.seniority_level}) - ${persona.industry}`);
    });

    if (personas.length > 0) {
      // Generate content for first persona
      const selectedPersona = personas[0];
      console.log(`\nGenerating content for: ${selectedPersona.role}`);
      
      const contentResult = await contentGenerator.generatePersonalizedContent(
        selectedPersona.id,
        'LinkedIn post',
        'Focus on the latest industry trends and how our solution addresses emerging challenges.'
      );

      console.log('\nGenerated content prompt:');
      console.log('=' .repeat(80));
      console.log(contentResult.prompt);
      console.log('=' .repeat(80));

      // Get content suggestions
      const suggestions = contentGenerator.getContentSuggestions(selectedPersona.id, 'awareness');
      console.log('\nContent suggestions for this persona:');
      suggestions.forEach((suggestion, index) => {
        console.log(`${index + 1}. ${suggestion}`);
      });
    }
  } catch (error) {
    console.error('Demo failed:', error);
  }
}

// Export for use in VoiceForge
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    GypsumVoiceForgeClient,
    VoiceForgeContentGenerator,
    demoVoiceForgeIntegration
  };
}

// Run demo if this file is executed directly
if (typeof window === 'undefined' && require.main === module) {
  demoVoiceForgeIntegration();
}
