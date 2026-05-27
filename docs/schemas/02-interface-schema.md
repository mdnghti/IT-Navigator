# Схема интерфейса IT Navigator

## Структура навигации

```mermaid
graph TB
    Landing[Landing Page]
    
    subgraph "Public Pages"
        Login[Login Page]
        Register[Register Page]
        About[About Page]
    end
    
    subgraph "Protected Pages"
        Dashboard[User Dashboard]
        
        subgraph "Testing Flow"
            GeneralTest[General Test]
            SpecializedTest[Specialized Test]
            TestProgress[Test Progress]
        end
        
        subgraph "Results"
            ResultsList[My Results]
            ResultDetail[Result Detail]
            ResultPDF[PDF Export]
        end
        
        subgraph "Profile"
            ProfileView[View Profile]
            ProfileEdit[Edit Profile]
        end
    end
    
    subgraph "Admin Panel"
        AdminDashboard[Admin Dashboard]
        AdminUsers[Manage Users]
        AdminTests[Manage Tests]
        AdminQuestions[Manage Questions]
        AdminSpecialties[Manage Specialties]
    end

    Landing --> Login
    Landing --> Register
    Landing --> About
    
    Login --> Dashboard
    Register --> Dashboard
    
    Dashboard --> GeneralTest
    Dashboard --> ResultsList
    Dashboard --> ProfileView
    
    GeneralTest --> TestProgress
    TestProgress --> ResultDetail
    
    ResultDetail --> SpecializedTest
    SpecializedTest --> TestProgress
    
    ResultsList --> ResultDetail
    ResultDetail --> ResultPDF
    
    ProfileView --> ProfileEdit
    
    Dashboard --> AdminDashboard
    AdminDashboard --> AdminUsers
    AdminDashboard --> AdminTests
    AdminDashboard --> AdminQuestions
    AdminDashboard --> AdminSpecialties
```

## Wireframes основных страниц

### 1. Landing Page

```mermaid
graph TB
    subgraph "Landing Page Layout"
        Header[Header: Logo + Navigation + Login/Register]
        Hero[Hero Section: Заголовок + CTA Button]
        Features[Features Section: 3 колонки преимуществ]
        HowItWorks[How It Works: Пошаговая инструкция]
        Testimonials[Testimonials: Отзывы пользователей]
        Footer[Footer: Links + Contacts]
    end
    
    Header --> Hero
    Hero --> Features
    Features --> HowItWorks
    HowItWorks --> Testimonials
    Testimonials --> Footer
```

**Компоненты:**
- **Header**: Навигация, кнопки входа/регистрации
- **Hero**: Главный заголовок "Найди свою IT-специальность", кнопка "Начать тест"
- **Features**: Карточки с преимуществами (адаптивное тестирование, детальная аналитика, рекомендации)
- **How It Works**: Шаги 1-2-3 с иконками
- **Footer**: Ссылки на соцсети, контакты, политика конфиденциальности

### 2. Dashboard

```mermaid
graph TB
    subgraph "Dashboard Layout"
        TopNav[Top Navigation: Logo + User Menu]
        
        subgraph "Main Content"
            Welcome[Welcome Section: Имя пользователя + статистика]
            
            subgraph "Action Cards"
                StartTest[Card: Начать общий тест]
                ContinueTest[Card: Продолжить тест]
                ViewResults[Card: Мои результаты]
            end
            
            subgraph "Recent Activity"
                RecentTests[Последние тесты]
                RecentResults[Последние результаты]
            end
            
            subgraph "Recommendations"
                NextSteps[Рекомендуемые действия]
                Specialties[Подходящие специальности]
            end
        end
        
        Sidebar[Sidebar: Navigation Menu]
    end
    
    TopNav --> Welcome
    Welcome --> StartTest
    Welcome --> ContinueTest
    Welcome --> ViewResults
    
    StartTest --> RecentTests
    ContinueTest --> RecentTests
    ViewResults --> RecentResults
    
    RecentTests --> NextSteps
    RecentResults --> Specialties
```

**Компоненты:**
- **Top Navigation**: Логотип, поиск, уведомления, аватар пользователя
- **Sidebar**: Меню навигации (Dashboard, Tests, Results, Profile, Admin)
- **Welcome Section**: Приветствие, статистика (пройдено тестов, средний балл)
- **Action Cards**: Крупные кнопки для основных действий
- **Recent Activity**: Таблица/список последних активностей
- **Recommendations**: Персонализированные рекомендации

### 3. Test Page (General/Specialized)

```mermaid
graph TB
    subgraph "Test Page Layout"
        TestHeader[Test Header: Название + Progress Bar]
        
        subgraph "Question Section"
            QuestionNumber[Вопрос N из M]
            QuestionText[Текст вопроса]
            
            subgraph "Answer Options"
                Option1[Radio/Checkbox: Вариант 1]
                Option2[Radio/Checkbox: Вариант 2]
                Option3[Radio/Checkbox: Вариант 3]
                Option4[Radio/Checkbox: Вариант 4]
            end
        end
        
        subgraph "Navigation"
            PrevButton[Кнопка: Назад]
            NextButton[Кнопка: Далее]
            SubmitButton[Кнопка: Завершить тест]
        end
        
        Sidebar[Sidebar: Навигация по вопросам]
    end
    
    TestHeader --> QuestionNumber
    QuestionNumber --> QuestionText
    QuestionText --> Option1
    Option1 --> Option2
    Option2 --> Option3
    Option3 --> Option4
    
    Option4 --> PrevButton
    PrevButton --> NextButton
    NextButton --> SubmitButton
```

**Компоненты:**
- **Test Header**: Название теста, прогресс-бар (X из Y вопросов)
- **Question Section**: Номер вопроса, текст вопроса, варианты ответов
- **Answer Options**: Radio buttons (один ответ) или Checkboxes (несколько ответов)
- **Navigation**: Кнопки навигации между вопросами
- **Sidebar**: Миниатюры всех вопросов с индикацией ответов (отвечен/не отвечен)
- **Timer** (опционально): Таймер прохождения теста

### 4. Results Page

```mermaid
graph TB
    subgraph "Results Page Layout"
        ResultHeader[Result Header: Дата + Тип теста]
        
        subgraph "Score Overview"
            TotalScore[Общий балл]
            ScoreChart[Radar Chart: Баллы по специальностям]
        end
        
        subgraph "Specialty Breakdown"
            Specialty1[F1: Программирование - 85%]
            Specialty2[F2: Администрирование - 72%]
            Specialty3[F3: Дизайн - 45%]
            SpecialtyN[F7: Управление - 60%]
        end
        
        subgraph "Recommendations"
            TopSpecialties[Топ-3 подходящие специальности]
            NextSteps[Рекомендуемые действия]
            SpecializedTestCTA[CTA: Пройти специализированный тест]
        end
        
        subgraph "Actions"
            DownloadPDF[Кнопка: Скачать PDF]
            ShareResults[Кнопка: Поделиться]
            RetakeTest[Кнопка: Пройти заново]
        end
    end
    
    ResultHeader --> TotalScore
    TotalScore --> ScoreChart
    ScoreChart --> Specialty1
    Specialty1 --> Specialty2
    Specialty2 --> Specialty3
    Specialty3 --> SpecialtyN
    
    SpecialtyN --> TopSpecialties
    TopSpecialties --> NextSteps
    NextSteps --> SpecializedTestCTA
    
    SpecializedTestCTA --> DownloadPDF
    DownloadPDF --> ShareResults
    ShareResults --> RetakeTest
```

**Компоненты:**
- **Result Header**: Дата прохождения, тип теста, общий балл
- **Score Chart**: Радар-диаграмма с баллами по всем специальностям
- **Specialty Breakdown**: Список специальностей с процентами и прогресс-барами
- **Recommendations**: Персонализированные рекомендации на основе результатов
- **Actions**: Кнопки для скачивания PDF, повторного прохождения

### 5. Admin Panel

```mermaid
graph TB
    subgraph "Admin Panel Layout"
        AdminNav[Admin Navigation: Dashboard + Models]
        
        subgraph "Model Management"
            ModelList[Model List View: Таблица записей]
            
            subgraph "CRUD Operations"
                CreateForm[Create Form]
                EditForm[Edit Form]
                DeleteConfirm[Delete Confirmation]
            end
            
            subgraph "Filters & Search"
                SearchBar[Search Bar]
                Filters[Filters Panel]
                Pagination[Pagination]
            end
        end
        
        subgraph "Statistics"
            UserStats[User Statistics]
            TestStats[Test Statistics]
            SystemHealth[System Health]
        end
    end
    
    AdminNav --> ModelList
    ModelList --> SearchBar
    SearchBar --> Filters
    Filters --> Pagination
    
    ModelList --> CreateForm
    ModelList --> EditForm
    ModelList --> DeleteConfirm
    
    AdminNav --> UserStats
    UserStats --> TestStats
    TestStats --> SystemHealth
```

**Компоненты:**
- **Admin Navigation**: Меню с моделями (Users, Tests, Questions, Answers, Specialties)
- **Model List**: Таблица с данными, сортировка, фильтры
- **CRUD Forms**: Формы создания/редактирования записей
- **Statistics**: Дашборд с метриками и графиками

## UI Components Library

### Базовые компоненты

```mermaid
graph LR
    subgraph "Atoms"
        Button[Button]
        Input[Input]
        Checkbox[Checkbox]
        Radio[Radio]
        Select[Select]
        Badge[Badge]
        Avatar[Avatar]
        Icon[Icon]
    end
    
    subgraph "Molecules"
        FormField[Form Field]
        Card[Card]
        Modal[Modal]
        Dropdown[Dropdown]
        Tooltip[Tooltip]
        Alert[Alert]
        ProgressBar[Progress Bar]
    end
    
    subgraph "Organisms"
        Header[Header]
        Sidebar[Sidebar]
        Form[Form]
        Table[Table]
        Chart[Chart]
        Pagination[Pagination]
    end
    
    Button --> FormField
    Input --> FormField
    Checkbox --> FormField
    Radio --> FormField
    
    FormField --> Form
    Card --> Table
    Icon --> Button
    Avatar --> Header
    
    Form --> Header
    Table --> Pagination
```

### Дизайн-система

**Цветовая палитра:**
- Primary: `#3B82F6` (Blue)
- Secondary: `#8B5CF6` (Purple)
- Success: `#10B981` (Green)
- Warning: `#F59E0B` (Orange)
- Error: `#EF4444` (Red)
- Background: `#0F172A` (Dark Blue)
- Surface: `#1E293B` (Dark Gray)
- Text: `#F1F5F9` (Light Gray)

**Типографика:**
- Heading 1: `32px / 2rem` - Bold
- Heading 2: `24px / 1.5rem` - Bold
- Heading 3: `20px / 1.25rem` - Semibold
- Body: `16px / 1rem` - Regular
- Small: `14px / 0.875rem` - Regular
- Caption: `12px / 0.75rem` - Regular

**Spacing:**
- xs: `4px`
- sm: `8px`
- md: `16px`
- lg: `24px`
- xl: `32px`
- 2xl: `48px`

**Border Radius:**
- sm: `4px`
- md: `8px`
- lg: `12px`
- xl: `16px`
- full: `9999px`

## Responsive Design

```mermaid
graph LR
    subgraph "Breakpoints"
        Mobile[Mobile: < 640px]
        Tablet[Tablet: 640px - 1024px]
        Desktop[Desktop: > 1024px]
    end
    
    subgraph "Layout Adaptations"
        MobileLayout[Mobile: Stack layout]
        TabletLayout[Tablet: 2-column grid]
        DesktopLayout[Desktop: 3-column grid + sidebar]
    end
    
    Mobile --> MobileLayout
    Tablet --> TabletLayout
    Desktop --> DesktopLayout
```

**Mobile (< 640px):**
- Hamburger menu
- Single column layout
- Touch-friendly buttons (min 44px)
- Bottom navigation bar

**Tablet (640px - 1024px):**
- Collapsible sidebar
- 2-column grid
- Adaptive cards

**Desktop (> 1024px):**
- Fixed sidebar
- 3-column grid
- Hover states
- Keyboard shortcuts

## Анимации и переходы

```mermaid
graph TB
    subgraph "Page Transitions"
        FadeIn[Fade In: 300ms]
        SlideIn[Slide In: 400ms]
        ScaleIn[Scale In: 200ms]
    end
    
    subgraph "Component Animations"
        Hover[Hover: Scale 1.05]
        Click[Click: Scale 0.95]
        Loading[Loading: Spin]
        Progress[Progress: Width transition]
    end
    
    subgraph "Micro-interactions"
        ButtonRipple[Button Ripple]
        CardFlip[Card Flip]
        ToastSlide[Toast Slide]
        ModalFade[Modal Fade]
    end
```

**Timing Functions:**
- Ease In: `cubic-bezier(0.4, 0, 1, 1)`
- Ease Out: `cubic-bezier(0, 0, 0.2, 1)`
- Ease In Out: `cubic-bezier(0.4, 0, 0.2, 1)`

## Accessibility (A11y)

```mermaid
graph TB
    subgraph "WCAG 2.1 AA Compliance"
        ColorContrast[Color Contrast: 4.5:1]
        KeyboardNav[Keyboard Navigation]
        ScreenReader[Screen Reader Support]
        FocusIndicators[Focus Indicators]
        AltText[Alt Text for Images]
        AriaLabels[ARIA Labels]
    end
    
    subgraph "Implementation"
        SemanticHTML[Semantic HTML]
        TabIndex[Tab Index Management]
        LiveRegions[Live Regions]
        ErrorMessages[Error Messages]
    end
    
    ColorContrast --> SemanticHTML
    KeyboardNav --> TabIndex
    ScreenReader --> AriaLabels
    FocusIndicators --> SemanticHTML
    AltText --> AriaLabels
    AriaLabels --> LiveRegions
```

**Требования:**
- Все интерактивные элементы доступны с клавиатуры
- Контраст текста минимум 4.5:1
- ARIA-метки для всех форм
- Фокус-индикаторы видимы
- Альтернативный текст для изображений
- Поддержка screen readers

## User Flow: Прохождение теста

```mermaid
stateDiagram-v2
    [*] --> Landing
    Landing --> Login: Клик "Войти"
    Landing --> Register: Клик "Регистрация"
    
    Login --> Dashboard: Успешный вход
    Register --> Dashboard: Успешная регистрация
    
    Dashboard --> GeneralTest: Клик "Начать тест"
    GeneralTest --> Question1: Загрузка вопросов
    
    Question1 --> Question2: Ответ + "Далее"
    Question2 --> Question3: Ответ + "Далее"
    Question3 --> QuestionN: ...
    
    QuestionN --> SubmitConfirm: Клик "Завершить"
    SubmitConfirm --> Processing: Подтверждение
    Processing --> Results: Расчет завершен
    
    Results --> SpecializedTest: Клик "Пройти специализированный"
    Results --> Dashboard: Клик "На главную"
    Results --> DownloadPDF: Клик "Скачать PDF"
    
    SpecializedTest --> Question1: Новый тест
    DownloadPDF --> Results: PDF сгенерирован
    
    Dashboard --> [*]: Выход
```

## Error States & Loading States

```mermaid
graph TB
    subgraph "Loading States"
        InitialLoad[Initial Load: Skeleton]
        DataFetch[Data Fetch: Spinner]
        FormSubmit[Form Submit: Button loading]
        PageTransition[Page Transition: Progress bar]
    end
    
    subgraph "Error States"
        NetworkError[Network Error: Retry button]
        ValidationError[Validation Error: Inline message]
        AuthError[Auth Error: Redirect to login]
        NotFound[404: Not found page]
        ServerError[500: Server error page]
    end
    
    subgraph "Empty States"
        NoData[No Data: Empty state illustration]
        NoResults[No Results: Search suggestions]
        NoTests[No Tests: CTA to start]
    end
```

**Обработка ошибок:**
- Inline validation для форм
- Toast notifications для успеха/ошибки
- Retry кнопки для network errors
- Fallback UI для критических ошибок
- Graceful degradation

## Темная тема (Dark Mode)

Система использует темную тему по умолчанию с возможностью переключения:

**Dark Theme (Default):**
- Background: `#0F172A`
- Surface: `#1E293B`
- Text: `#F1F5F9`

**Light Theme (Optional):**
- Background: `#FFFFFF`
- Surface: `#F8FAFC`
- Text: `#0F172A`

Переключение через `prefers-color-scheme` и localStorage.
