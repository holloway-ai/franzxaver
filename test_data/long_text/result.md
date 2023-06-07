## Introduction
I'm Colleen Farley. I live in Miami, Florida. I am the author of *The Shape of Data*, which will be coming out this next year. And I've focused a lot on public health, social sciences, and a lot of mathematical tools that can be used to study both of these. 

## Tools
So let's go through some of the tools. We're not going to get into details here too much. Just kind of what the tools are and how we can use them. 

### Persistent Homology
The first tool is something called **persistent homology**, which comes from a branch of math called topology. This branch is not real concerned with how your data is put together in the local sense. It's more about how your data is connected. So basically we create a series of distance-based objects and look at features across them. This does connect back to geometry and the curvature and the distances that you define in your data. But it's a little broader of an overview. 

### Furman-Ritchie Curvature
The next tool is **Furman-Ritchie curvature**, which is a network science metric. We just had a great two presentations on network science and how useful it is. This tool measures the curvature on the graph. So in physics, when we have a lot of matter in the same spot, it pulls everything towards it. So black holes are going to pull planets towards it, pull your spaceship towards it. And the same thing happens in networks. When we have a lot of things that are connected in the same area of the graph, processes that happen on a graph tend to get pulled into there. So if you're looking at marketing campaigns, it tends to clump around that area. If you're looking at epidemics, that's typically where you're going to find a lot of cases. And in general, this is a very useful tool for understanding change points and behavior over time on graphs. 

## Generative AI
There's a newer branch of machine learning that's been really useful. **Generative AI** and some of the geometry tools that evolve these creations have been playing a major role in having people being able to develop things through AI without actually having to know much coding. So basically there's a deep learning algorithm that can take your text and create an image.


![{~1.47}](https://d8kx9lltbn9tr.cloudfront.net/joan/videos/945d9259-6c03-4767-adac-6a8105d106a3/slides/44.png)


![{~4.43}](https://d8kx9lltbn9tr.cloudfront.net/joan/videos/945d9259-6c03-4767-adac-6a8105d106a3/slides/133.png)


![{~16.73}](https://d8kx9lltbn9tr.cloudfront.net/joan/videos/945d9259-6c03-4767-adac-6a8105d106a3/slides/502.png)


![{~33.03}](https://d8kx9lltbn9tr.cloudfront.net/joan/videos/945d9259-6c03-4767-adac-6a8105d106a3/slides/991.png)


![{~88.27}](https://d8kx9lltbn9tr.cloudfront.net/joan/videos/945d9259-6c03-4767-adac-6a8105d106a3/slides/2648.png)


![{~164.77}](https://d8kx9lltbn9tr.cloudfront.net/joan/videos/945d9259-6c03-4767-adac-6a8105d106a3/slides/4943.png)

{~168.08}And there are tools in geometry that are able to evolve and kind of massage out what you  {~176.24}{~176.24}want from the image.  {~178.32}{~178.32}This is an example on the left of a place that does not actually exist.  {~183.52}{~183.52}But I created it with one of the open source tools out there.  {~187.52}{~187.52}And this can be really useful, as we'll see.{~193.14000000000001}

## Applications
So let's get into the applications.  A few of the projects that I've used persistent homology on are looking at urban growth tipping  points.  So as cities grow, especially if there's not a lot of infrastructure or planning going  on when cities start evolving, we can run into problems with infrastructure, we can  run into problems with public health and sanitation, and we can end up with environmental issues  if there's a tipping point that results in a lot of growth without enough time to build  all of the things needed to keep a city running.


![{~193.53}](https://d8kx9lltbn9tr.cloudfront.net/joan/videos/945d9259-6c03-4767-adac-6a8105d106a3/slides/5806.png)


![{~245.50}](https://d8kx9lltbn9tr.cloudfront.net/joan/videos/945d9259-6c03-4767-adac-6a8105d106a3/slides/7365.png)

{~233.66}We can also look at climate change and understand when there are points of no return, when the  {~240.28}{~240.28}climate is going to tip, when populations aren't safe living in an area anymore.  {~244.72}{~244.72}And this is really important to be able to relocate populations before a disaster happens  {~250.36}{~250.36}in their area or before the area is unlivable, such as barrier islands, communities on rivers,  {~259.88}{~259.88}areas near the Sahara, which are dealing with a lot of deforestation and evolution into  {~267.52}{~267.52}desert climates.{~269.56}

## Understanding Epidemic Growth

{~269.56}In addition, with the recent COVID epidemic, this is also really important in understanding{~276.32} {~276.32}epidemic growth so that we can position resources, especially in communities that may not have{~282.4} {~282.4}a lot of starting resources.{~285.12} {~285.12}Being able to understand where and when we need to place these resources can go a long{~289.8} {~289.8}way in preventing the spread of an epidemic and limiting the loss of life during one.{~297.64}

## Norman Ricci Curvature

{~297.64}Norman Ricci curvature is another tool that I use a lot in my work.{~303.71999999999997}

## Crisis in Food Prices

{~303.71999999999997}Right now, there's a huge crisis in food prices.{~307.64} {~307.64}So this is impacting a lot of communities.{~310.96} {~310.96}Middle class populations are finding themselves being driven back into poverty with rising{~315.7} {~315.7}food prices.{~317.52} {~317.52}And there's a lot of food insecurity that has started, especially since the Ukraine{~321.47999999999996} {~321.47999999999996}conflict.{~323.08} {~323.08}So understanding when prices are going to change, what prices are going to change, and{~328.0} {~328.0}where they're going to change allows social programs to be able to meet these needs.{~333.84} {~333.84}It allows food aid programs to be able to know how much aid they may need to meet the{~341.15999999999997} {~341.15999999999997}need of the communities, as well as what governments can do locally to reduce the price of food{~347.76} {~347.76}and help populations get through rough patches.{~352.08}

## Using Models During the DR Congo 2018 Ebola Outbreak


![{~369.53}](https://d8kx9lltbn9tr.cloudfront.net/joan/videos/945d9259-6c03-4767-adac-6a8105d106a3/slides/11086.png)

{~352.08}One of the first times that I used these models on a project was during the DR Congo 2018{~359.15999999999997} {~359.15999999999997}Ebola outbreak.{~361.64} {~361.64}The outbreak happened in an under-resourced area of the country, and getting resources{~368.46} {~368.46}in the areas impacted was difficult for NGOs and for local responders.{~375.47999999999996} {~375.48}And being able to understand where and when the next wave of the epidemic would hit helped{~382.64000000000004} {~382.64000000000004}be able to position those resources to respond accordingly and in areas of greatest need.{~389.94}

## Understanding Social Networks

{~389.94}There's another use, more common in marketing, but also with behavior change, of understanding{~397.56} {~397.56}where in a social network or a geographic network an intervention can be done.{~403.66} {~403.66}So say you want to have a smoking cessation program or a sexual health education program{~411.64000000000004} {~411.64000000000004}that tips behavior change at a population level.{~416.68} {~416.68}Understanding how your network is put together and who has the influence in the network to{~422.32000000000005} {~422.32000000000005}be able to impact change on a population level without having the resources to intervene{~427.12} {~427.12}on everyone, having these type of tools is really, really useful to be able to selectively{~434.2} {~434.2}target different populations or different individuals within the population to affect{~440.4} {~440.4}the system level change.{~445.7}

{~445.7}So last we have generative AI.{~449.78000000000003} {~449.78000000000003}One of the things that I've found is that this is very useful in public health education.{~454.22} {~454.22}So during the COVID outbreak, we had mass campaigns, vaccination campaigns to try to{~460.1} {~460.1}help improve population health and protect vulnerable populations.{~465.14000000000004} {~465.14000000000004}However, there are a lot of caveats with doing public health in remote places with certain{~473.34000000000003} {~473.34000000000003}populations.{~475.66} {~475.66}Being able to make something culturally relevant is really important.{~480.42} {~480.42}To people who look like the community, being the image or the person speaking is really{~488.74} {~488.74}important to be relatable.{~492.04} {~492.04}And generative AI allows us to create culturally relevant images for these campaigns.{~498.66} {~498.66}In addition, they're really useful as a way to be able to do this with under-resourced{~505.38} {~505.38}areas, areas that don't have maybe as much infrastructure around creating videos, creating{~516.26} {~516.26}image campaigns, creating public service announcements.{~519.7} {~519.7}Having this technology allows the resources to go further.{~524.42} {~524.42}Long time ago, when I was working on HIV education in South Africa, there wasn't a lot to go{~532.82} {~532.82}on and a lot of it had to be developed on the fly.{~536.0200000000001} {~536.0200000000001}And that's very hard to do when you're in a rural community.{~539.62} {~539.62}It's a lot of finding people, positioning, whatever skit or whatever materials need to{~547.0600000000001} {~547.0600000000001}be created, actually creating those materials.{~550.38} {~550.38}It used to take a lot of time 20 years ago.{~554.3000000000001} {~554.3000000000001}But now with generative AI, we can tell our algorithm what we want to generate, generate{~561.58} {~561.58}10 images or 100 images, and then look through them for what's most likely to resonate with{~568.9000000000001}{~568.9000000000001} the population.{~570.34}## Introduction
And that's really impactful. And I think in the future, we're going to be seeing a lot more of these technologies being leveraged in fields that might not have used these, in marketing, in public health, in social program awareness campaigns, pretty much anything that needs to get the information out, particularly in a visual manner.


![{~540.03}](https://d8kx9lltbn9tr.cloudfront.net/joan/videos/945d9259-6c03-4767-adac-6a8105d106a3/slides/16201.png)

{~596.02}So a lot of areas of the world have a lot of local languages.{~601.02} {~601.02}And somebody who is a native speaker of that language might know some of the more dominant{~606.5400000000001} {~606.5400000000001}language messages can get lost in translation.{~611.86} {~611.86}Or there might be a need to hire a lot of translators to get the information out there.{~617.38} {~617.38}And this technology promises to really help solve a lot of those barriers to public health{~625.86} {~625.86}interventions, social policy announcements, even just getting information about what resources{~632.84} {~632.84}exist to these populations.{~637.96}

## Importance of Representation
So one of the things that I'm really passionate about is the need for representation. So if we don't collect data on people who look a certain way or speak a certain language or come from a certain area of the country or the world, we don't have that data for our algorithms to learn from. And those populations may not have their needs met. If we don't have that representation on tech teams, we don't have that perspective of how there might be barriers to adopting the technology or having the technology work correctly within that population. So it's really important that we consider different cultures and different subgroups so that everyone can participate.


![{~675.43}](https://d8kx9lltbn9tr.cloudfront.net/joan/videos/945d9259-6c03-4767-adac-6a8105d106a3/slides/20263.png)

{~680.3}I think we're at a tipping point within tech of those who are benefiting a lot from it{~686.5799999999999} {~686.5799999999999}and those that haven't benefited much.{~689.12} {~689.12}And if we keep going this way and some populations have a lot more representation than others,{~695.02} {~695.02}I think we're going to be seeing more and more division along the lines of technology.{~699.48} {~699.48}So that's really important, especially within social good projects that we have representation{~705.22} {~705.22}from the community, that the community has ownership in data, input into how this is{~711.18} {~711.18}going to be used or impact their community.{~716.1}

## Resources
So there are a lot of good resources out there. I'm going to make this presentation public on my LinkedIn. So feel free to reach out to me. Feel free to look at these resources for the tools that are out there. 

- {~733.54}Persistent Homology has a lot of packages that exist in R and Python.{~739.74} 
- {~733.54}{~739.74}{~739.74}Text to image, OpenAI and Night Cafe have some really great tools.{~745.46} 
- {~739.74}{~745.46}{~745.46}For Forman Ritchie Curvature, I have code in Python and in R for different network applications.{~752.74}


![{~734.50}](https://d8kx9lltbn9tr.cloudfront.net/joan/videos/945d9259-6c03-4767-adac-6a8105d106a3/slides/22035.png)

{~752.74}And feel free to reach out to me.{~754.9}
![{~756.10}](https://d8kx9lltbn9tr.cloudfront.net/joan/videos/945d9259-6c03-4767-adac-6a8105d106a3/slides/22683.png)
![{~758.90}](https://d8kx9lltbn9tr.cloudfront.net/joan/videos/945d9259-6c03-4767-adac-6a8105d106a3/slides/22767.png)