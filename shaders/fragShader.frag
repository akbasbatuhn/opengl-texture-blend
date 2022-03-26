#version 330

in vec4 fragColor;
in vec2 fragUV;

out vec4 outColor;

uniform sampler2D tex1;
uniform sampler2D tex2;
uniform float value;

void main()
{
   vec4 texVal1 = texture(tex1, fragUV);
   vec4 texVal2 = texture(tex2, fragUV);
   outColor = fragColor * ((1 - value) * texVal1 + value * texVal2);
}