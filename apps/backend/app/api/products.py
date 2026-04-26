from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db.session import get_db
from app.models.user import User
from app.models.product import Product
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse
)
from app.utils.auth import get_current_user
from app.services.audit_service import log_audit
from typing import Optional
import uuid
import math

router = APIRouter(prefix="/api/products", tags=["Products"])


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new product/inventory item
    
    - **name**: Product name (required)
    - **description**: Product description
    - **unit**: Unit of measurement (nos, kg, ltr, sqft, Ton, etc.)
    - **default_price**: Default price per unit
    - **gst_rate**: GST rate percentage (default: 18%)
    """
    # Create product
    product = Product(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        **product_data.model_dump()
    )
    
    db.add(product)
    db.commit()
    db.refresh(product)
    
    # Audit log
    log_audit(
        db=db,
        user_id=current_user.id,
        action="product.created",
        entity_type="product",
        entity_id=product.id,
        new_value={"name": product.name, "price": float(product.default_price) if product.default_price else None}
    )
    
    return product


@router.get("", response_model=ProductListResponse)
async def list_products(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(default=None, description="Search in name/description"),
    is_active: Optional[bool] = Query(default=None, description="Filter by active status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all products for the current user with pagination and search
    
    - **page**: Page number (starts from 1)
    - **page_size**: Number of items per page (max 100)
    - **search**: Search query for name/description
    - **is_active**: Filter by active status
    """
    # Build query
    query = db.query(Product).filter(Product.user_id == current_user.id)
    
    # Apply filters
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Product.name.like(search_pattern),
                Product.description.like(search_pattern)
            )
        )
    
    if is_active is not None:
        query = query.filter(Product.is_active == is_active)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    products = query.order_by(Product.created_at.desc()).offset(offset).limit(page_size).all()
    
    # Calculate total pages
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    
    return ProductListResponse(
        products=products,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific product by ID"""
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    product_data: ProductUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing product
    
    All fields are optional - only provided fields will be updated
    """
    # Find product
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Store old values for audit
    old_values = {
        "name": product.name,
        "default_price": float(product.default_price) if product.default_price else None,
        "is_active": product.is_active
    }
    
    # Update fields
    update_data = product_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    
    # Audit log
    new_values = {
        "name": product.name,
        "default_price": float(product.default_price) if product.default_price else None,
        "is_active": product.is_active
    }
    log_audit(
        db=db,
        user_id=current_user.id,
        action="product.updated",
        entity_type="product",
        entity_id=product.id,
        old_value=old_values,
        new_value=new_values
    )
    
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a product
    
    Note: This performs a hard delete. Consider using is_active=False instead.
    """
    # Find product
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Audit log
    log_audit(
        db=db,
        user_id=current_user.id,
        action="product.deleted",
        entity_type="product",
        entity_id=product.id,
        old_value={"name": product.name}
    )
    
    # Delete
    db.delete(product)
    db.commit()
    
    return None
